module globalPred (
    input wire clk, rst,
    
    input wire flushD,
    input wire stallD,

    input wire [31:0] pcF,
    input wire [31:0] pcM,

    input wire branchM,         // M阶段是否是分支指令
    input wire actual_takeM,    // 实际是否跳转
    input wire pred_takeM,      // M阶段的指令预测是否跳转

    input wire branchD,        // 译码阶段是否是跳转指令   
    output wire pred_takeD      // 预测是否跳转
);
    // 定义参数
    parameter Strongly_not_taken = 2'b00, Weakly_not_taken = 2'b01, Weakly_taken = 2'b11, Strongly_taken = 2'b10;
    parameter GHR_WIDTH = 6;
    parameter GPHT_DEPTH = 9;
    integer i;
    // 定义全局预测表
    reg [1:0] GPHT [(1 << GHR_WIDTH) - 1 : 0];
    // 定义GHR和RE_GHR
    reg [GHR_WIDTH - 1 : 0] GHR;
    reg [GHR_WIDTH - 1 : 0] RE_GHR;
    // 线网定义
    assign GHR_VALUE = GHR;
    assign GPHT_INDEX = {pcF[4:2], GHR};
    assign pred_takeF = GPHT[GPHT_INDEX][1];
    assign fail_Pred = pred_takeM ^ actual_takeM;   // 为1则预测失败
    // 定义预测寄存器
    reg pred_takeF_r;
// -----------------------pipeline result--------------------------------
    always @(posedge ~clk) begin
        if (rst | flushD) begin
            pred_takeF_r <= 0;
        end
        else if (~stallD) begin
            pred_takeF_r <= pred_takeF;
        end
        else begin
            pred_takeF_r <= pred_takeF_r;
        end
    end
// -----------------------------GHR初始化以及更新--------------------------
    always @(posedge ~clk) begin
        if (rst) begin
            GHR <= 0;
        end
        else if (branchM & fail_Pred) begin   // 异或结果不为0，说明预测错误，需要RE_GHR更新，进入ID,EX的指令需要全部清刷掉（flush信号），PC连上正确的地址！
            GHR <= {RE_GHR[GHR_WIDTH-1:1], actual_takeM};
        end
        else if (branchD) begin     // 前面ID阶段的指令是分支指令，保存预测记录
            GHR <= {GHR[GHR_WIDTH-2 : 0], pred_takeF};
        end
        else begin  // 前面ID阶段的指令不是分支指令，直接覆盖上个周期的预测结果
            GHR <= {GHR[GHR_WIDTH-1 : 1], pred_takeF};
        end
    end
// -----------------------------RE_GHR初始化以及更新--------------------------
    always @(posedge ~clk) begin
        if (rst) begin
            RE_GHR <= 0;
        end
        else if (branchM) begin     // 是分支指令
            RE_GHR <= {RE_GHR[GHR_WIDTH-2 : 0], actual_takeM};
        end
        else begin
            RE_GHR <= RE_GHR;
        end
    end
// ----------------------------GPHT初始化以及更新---------------------------
    assign update_GPHT_index = {pcM[4:2], RE_GHR};
    always @(posedge ~clk) begin
        if (rst) begin
            for (i = 0; i < (1 << GHR_WIDTH) - 1; i = i + 1) begin
                GPHT[i] = 0;
            end
        end
        else if (branchM) begin     // 提交阶段进行更新
            case(GPHT[update_GPHT_index])
                Strongly_taken: GPHT[update_GPHT_index] <= actual_takeM == 1'b1 ? Strongly_taken : Weakly_taken;
                Strongly_not_taken: GPHT[update_GPHT_index] <= actual_takeM == 1'b1 ? Weakly_not_taken : Strongly_not_taken;
                Weakly_not_taken: GPHT[update_GPHT_index] <= actual_takeM == 1'b1 ? Strongly_taken : Strongly_not_taken;
                Weakly_taken: GPHT[update_GPHT_index] <= actual_takeM == 1'b1 ? Strongly_taken : Strongly_not_taken;
                default: GPHT[update_GPHT_index] <= 2'b00;
            endcase
        end
    end
// -------------------------译码阶段判断是否是分支指令并跳转----------------------
    assign pred_takeD = branchD & pred_takeF_r;
endmodule