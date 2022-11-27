module i_cache (
    input wire clk, rst,
    //mips core
    input         cpu_inst_req     ,
    input         cpu_inst_wr      ,
    input  [1 :0] cpu_inst_size    ,
    input  [31:0] cpu_inst_addr    ,
    input  [31:0] cpu_inst_wdata   ,
    output [31:0] cpu_inst_rdata   ,
    output        cpu_inst_addr_ok ,
    output        cpu_inst_data_ok ,

    //axi interface
    output         cache_inst_req     ,
    output         cache_inst_wr      ,
    output  [1 :0] cache_inst_size    ,
    output  [31:0] cache_inst_addr    ,
    output  [31:0] cache_inst_wdata   ,
    input   [31:0] cache_inst_rdata   ,
    input          cache_inst_addr_ok ,         // axi接收到地址
    input          cache_inst_data_ok           // 返回了data
);
    //Cache配置
    parameter  INDEX_WIDTH  = 10, OFFSET_WIDTH = 2, WAY_WIDTH = 2;
    localparam TAG_WIDTH    = 32 - INDEX_WIDTH - OFFSET_WIDTH;
    localparam CACHE_DEEPTH = 1 << INDEX_WIDTH;
    localparam WAY_NUM = 1 << WAY_WIDTH;
    
    // 由于语法问题不得不前置的变量
    reg [WAY_WIDTH - 1 : 0] victim_index;
    reg [WAY_WIDTH - 1 : 0] choose_way_save;
    //Cache存储单元
    reg                 cache_valid[WAY_NUM - 1 : 0][CACHE_DEEPTH - 1 : 0];
    reg                 cache_dirty[WAY_NUM - 1 : 0][CACHE_DEEPTH - 1 : 0];
    reg [TAG_WIDTH-1:0] cache_tag  [WAY_NUM - 1 : 0][CACHE_DEEPTH - 1 : 0];
    reg [31:0]          cache_block[WAY_NUM - 1 : 0][CACHE_DEEPTH - 1 : 0];
    reg [WAY_NUM - 2:0] tree_table                  [CACHE_DEEPTH - 1 : 0];

    //访问地址分解
    wire [OFFSET_WIDTH-1:0] offset;
    wire [INDEX_WIDTH-1:0] index;
    wire [TAG_WIDTH-1:0] tag;
    
    assign offset = cpu_inst_addr[OFFSET_WIDTH - 1 : 0];
    assign index = cpu_inst_addr[INDEX_WIDTH + OFFSET_WIDTH - 1 : OFFSET_WIDTH];
    assign tag = cpu_inst_addr[31 : INDEX_WIDTH + OFFSET_WIDTH];

    //访问Cache line
    reg [WAY_NUM - 1 : 0] c_valid;
    reg [WAY_NUM - 1 : 0] c_dirty;
    reg [TAG_WIDTH-1:0] c_tag [WAY_NUM - 1 : 0];
    reg [31:0] c_block [WAY_NUM - 1 : 0];
    wire [WAY_NUM - 2 : 0] c_tree;
    integer c_way_index;
    // 组合逻辑描述各路取值状况
    assign c_tree = tree_table[index];
    always @(*) begin
        if (rst) begin
            for (c_way_index = 0; c_way_index < WAY_NUM ; c_way_index = c_way_index + 1) begin
                c_valid[c_way_index]  = 1'b0;
                c_dirty[c_way_index]  = 1'b0;
                c_tag[c_way_index]    = 0;
                c_block[c_way_index]  = 0;
            end
        end
        else begin
            for (c_way_index = 0; c_way_index < WAY_NUM ; c_way_index = c_way_index + 1) begin
                c_valid[c_way_index]  = cache_valid[c_way_index][index];
                c_dirty[c_way_index]  = cache_dirty[c_way_index][index];
                c_tag  [c_way_index]  = cache_tag  [c_way_index][index];
                c_block[c_way_index]  = cache_block[c_way_index][index];
            end
        end
    end

    //判断是否命中
    reg [WAY_NUM - 1 : 0] w_hit, w_miss;    // 各路的命中情况
    reg [WAY_WIDTH - 1 : 0] hit_index;       // 命中所在的路下标
    wire [WAY_WIDTH - 1 : 0] choose_way;
    wire hit, miss;                         // 所有路是否有命中的，全未命中则miss为1
    wire dirty, valid;
    wire [31:0] wc_block;
    integer signal_way_index;
    always @(*) begin
        if (rst) begin
            w_hit       = 0;
            w_miss      = 0;
            hit_index   = 0;
        end
        else begin
            for (signal_way_index = 0; signal_way_index < WAY_NUM ; signal_way_index = signal_way_index + 1) begin
                w_hit[signal_way_index]     = c_valid[signal_way_index] & (c_tag[signal_way_index] == tag);
                w_miss[signal_way_index]    = ~w_hit[signal_way_index];
                hit_index                   = w_hit[signal_way_index] == 1'b1 ? signal_way_index : hit_index;       // 命中的路数
            end
        end
    end
    assign hit  = |w_hit;        //存在命中的则为命中信号，注意这里有个位缩减运算符
    assign miss = ~hit;
    assign dirty = hit ? c_dirty[hit_index] : c_dirty[victim_index];
    assign valid = hit ? c_valid[hit_index] : c_valid[victim_index];
    assign wc_block = c_block[choose_way];
    assign choose_way = hit ? hit_index : victim_index;
    //读或写
    wire    read, write;
    assign  write   = cpu_inst_wr;
    assign  read    = ~write;


    // 鉴别状态
    reg in_RM;
    // FSM有限状态机
    parameter IDLE = 2'b00, RM = 2'b01;
    reg [1:0] state;
    always @(posedge clk) begin
        if(rst) begin
            state <= IDLE;
            in_RM <= 1'b0;
        end
        else begin
            case(state)
                IDLE:   
                begin
                    state <= cpu_inst_req & (hit | write & ~hit & ~dirty)   ?   IDLE  :
                             cpu_inst_req & read & ~hit & ~dirty        ?   RM    :
                    in_RM <= 1'b0;
                end
                RM:
                begin
                    state <= cache_inst_data_ok  ? IDLE : RM;
                    in_RM <= 1'b1;
                end
            endcase
        end
    end

    //读内存，为端口信号做准备
    //变量read_req, addr_rcv, read_finish用于构造类sram信号。
    wire read_req;      //一次完整的读事务，从发出读请求到结束
    reg addr_rcv;       //地址接收成功(addr_ok)后到结束, 1表示握手成功（和MEMORY）
    wire read_finish;   //数据接收成功(data_ok)，即读请求结束，1表示
    always @(posedge clk) begin
        addr_rcv <= rst ? 1'b0 :
                    read & cache_inst_req & cache_inst_addr_ok ? 1'b1 :
                    read_finish ? 1'b0 : addr_rcv;
    end
    assign read_req = state==RM;
    assign read_finish = read & cache_inst_data_ok;     //1表示从Memory读完了

    //写内存，为端口信号做准备
    wire write_req;     
    reg waddr_rcv;      
    wire write_finish;   
    always @(posedge clk) begin
        waddr_rcv <= rst ? 1'b0 :
                     write & cache_inst_req & cache_inst_addr_ok ? 1'b1 :
                     write_finish ? 1'b0 : waddr_rcv;
    end
    assign write_req = 1'b0;
    assign write_finish = write & cache_inst_data_ok;   //1表示已经向Memory写完了

    //output to mips core
    assign cpu_inst_rdata   = hit ? c_block[choose_way] : cache_inst_rdata;          // hit命中就算读命中，否则读缺失，读取cache的data上来
    assign cpu_inst_addr_ok = cpu_inst_req & hit | cache_inst_req & cache_inst_addr_ok ;
    assign cpu_inst_data_ok = cpu_inst_req & hit | cache_inst_data_ok ;

    //output to axi interface
    assign cache_inst_req   =   read_req & ~addr_rcv | write_req & ~waddr_rcv;
    assign cache_inst_wr    =   write_req;
    assign cache_inst_size  =   cpu_inst_size;
    assign cache_inst_addr  =   cache_inst_wr ? {c_tag[choose_way_save], index, offset}:
                                                cpu_inst_addr;
    assign cache_inst_wdata =   wc_block;           // 写回是从cache读出去，到内存中

    //写入Cache
    //保存地址中的tag, index，防止addr发生改变
    reg [TAG_WIDTH-1:0] tag_save;
    reg [INDEX_WIDTH-1:0] index_save;
    always @(posedge clk) begin
        tag_save   <= rst ? 0 :
                      cpu_inst_req ? tag : tag_save;
        index_save <= rst ? 0 :
                      cpu_inst_req ? index : index_save;
    end

    wire [31:0] write_cache_data;
    wire [3:0] write_mask;

    //根据地址低两位和size，生成写掩码（针对sb，sh等不是写完整一个字的指令），4位对应1个字（4字节）中每个字的写使能
    // write-mask 1位对应对应的字节
    assign write_mask = cpu_inst_size==2'b00 ?
                            (cpu_inst_addr[1] ? (cpu_inst_addr[0] ? 4'b1000 : 4'b0100):
                                                (cpu_inst_addr[0] ? 4'b0010 : 4'b0001)) :
                            (cpu_inst_size==2'b01 ? (cpu_inst_addr[1] ? 4'b1100 : 4'b0011) : 4'b1111);

    //掩码的使用：位为1的代表需要更新的。
    //位拓展：{8{1'b1}} -> 8'b11111111
    //new_data = old_data & ~mask | write_data & mask
    assign write_cache_data = wc_block & ~{{8{write_mask[3]}}, {8{write_mask[2]}}, {8{write_mask[1]}}, {8{write_mask[0]}}} |       //这个写进Cache的原因预测与57条指令有关，先别动
                              cpu_inst_wdata & {{8{write_mask[3]}}, {8{write_mask[2]}}, {8{write_mask[1]}}, {8{write_mask[0]}}};            // 从cpu来的data

    // 读，写缺失，需要选择一个Victim Block
    reg  [31:0] write_cache_inst_save;
    always @(*) begin
        if (rst) begin
            victim_index = 0;
        end
        else if (miss & cpu_inst_req) begin
            victim_index = c_tree == 3'b000 ? 2'b11 : 
                           c_tree == 3'b001 ? 2'b10 :
                           c_tree == 3'b010 ? 2'b11 :
                           c_tree == 3'b011 ? 2'b10 :
                           c_tree == 3'b100 ? 2'b01 :
                           c_tree == 3'b101 ? 2'b01 :
                           c_tree == 3'b110 ? 2'b00 :
                                              2'b00 ;
        end
        else begin
            victim_index = victim_index;
        end
    end
    // 保存victim_index及写入的数据
    always @(posedge clk) begin
        write_cache_inst_save <= rst ? 0 : cpu_inst_req ? write_cache_data : write_cache_inst_save;
        choose_way_save <= rst? 0 : cpu_inst_req ? choose_way : choose_way_save;
    end

    integer t, s;
    always @(posedge clk) begin     // 修改cache_valid的具体位置
        if(rst) begin
            for(t = 0; t < CACHE_DEEPTH; t = t + 1) begin   //刚开始将Cache置为无效，以及dirty位置为0
                for (s = 0; s < WAY_NUM; s = s + 1) begin
                    cache_valid[s][t] <= 0;
                    cache_dirty[s][t] <= 0;
                    cache_block[s][t] <= 0;
                    cache_tag  [s][t] <= 0;
                end
                tree_table [t]    <= 0;
            end
        end
        else begin
            if(read_finish & in_RM) begin //读缺失，访存结束时，read隐含之意就是缺失了,read_finish就是对于cache,Memory的数据读出来了
            // 特别要注意！要从RM回来才写，不然可能发生意想不到的错误
                cache_valid[choose_way][index] <= 1'b1;             //将Cache line置为有效
                cache_dirty[choose_way][index] <= 1'b0;
                cache_tag  [choose_way][index] <= tag_save;
                cache_block[choose_way][index] <= cache_inst_rdata; //写入Cache line
            end
        end
        if (cpu_inst_req & hit) begin   // 没有Hit的话就别更新了，找到victim_block替换后，hit了再更
            tree_table[index] <= choose_way == 2'b00 ? 
                                    tree_table[index][2] == 1'b0 ? 3'b000 : 3'b001 :
                                 choose_way == 2'b01 ?
                                    tree_table[index][2] == 1'b0 ? 3'b010 : 3'b011 :
                                 choose_way == 2'b10 ?
                                    tree_table[index][1] == 1'b0 ? 3'b100 : 3'b110 :
                                    tree_table[index][1] == 1'b0 ? 3'b101 : 3'b111 ;
        end
    end
endmodule
