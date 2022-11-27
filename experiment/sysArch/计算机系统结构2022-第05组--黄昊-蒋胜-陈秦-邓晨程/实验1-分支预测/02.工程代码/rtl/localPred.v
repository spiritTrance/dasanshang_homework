module localPred(
    input wire clk, rst,
    
    input wire flushD,
    input wire stallD,

    input wire [31:0] pcF,
    input wire [31:0] pcM,

    input wire branchM,
    input wire actual_takeM,

    input wire branchD,
    output wire pred_takeD
);

// 线网和寄存器定义
    wire pred_takeF;
    reg pred_takeF_r;

// 参数定义
    parameter Strongly_not_taken = 2'b00, Weakly_not_taken = 2'b01, Weakly_taken = 2'b11, Strongly_taken = 2'b10;
    parameter PHT_DEPTH = 9;        // 6 + pc[4:2]
    parameter BHT_DEPTH = 10;

// 
    reg [5:0] BHT [(1<<BHT_DEPTH)-1 : 0];
    reg [1:0] PHT [(1<<PHT_DEPTH)-1 : 0];
    
    integer i,j;
    wire [(PHT_DEPTH-1):0] PHT_index;
    wire [(BHT_DEPTH-1):0] BHT_index;
    wire [(PHT_DEPTH-1):0] BHR_value;

// 预测逻辑

    assign BHT_index = pcF[11:2];     
    assign BHR_value = BHT[BHT_index];  
    assign PHT_index = {pcF[4:2], BHR_value};

    assign pred_takeF = PHT[PHT_index][1];

        // --------------------------pipeline------------------------------
            always @(posedge ~clk) begin
                if(rst | flushD) begin
                    pred_takeF_r <= 0;
                end
                else if(~stallD) begin
                    pred_takeF_r <= pred_takeF;
                end
            end
        // --------------------------pipeline------------------------------



// BHT更新
    wire [(PHT_DEPTH-1):0] update_PHT_index;
    wire [(BHT_DEPTH-1):0] update_BHT_index;
    wire [(PHT_DEPTH-1):0] update_BHR_value;

    assign update_BHT_index = pcM[11:2];     
    assign update_BHR_value = BHT[update_BHT_index];  
    assign update_PHT_index = {pcM[4:2], update_BHR_value};

    always@(posedge ~clk) begin
        if(rst) begin
            for(j = 0; j < (1 << BHT_DEPTH); j = j + 1) begin
                BHT[j] <= 0;
            end
        end
        else if(branchM) begin
            BHT[update_BHT_index] <= {BHT[update_BHT_index][4:0], actual_takeM};
        end
    end

// PHT更新
    always @(posedge ~clk) begin            
        if(rst) begin
            for(i = 0; i < (1<<PHT_DEPTH); i=i+1) begin
                PHT[i] <= Weakly_not_taken;
            end
        end
        else if (branchM) begin
            case(PHT[update_PHT_index])
                Strongly_taken: PHT[update_PHT_index] <= actual_takeM == 1'b1 ? Strongly_taken : Weakly_taken;
                Strongly_not_taken: PHT[update_PHT_index] <= actual_takeM == 1'b1 ? Weakly_not_taken : Strongly_not_taken;
                Weakly_not_taken: PHT[update_PHT_index] <= actual_takeM == 1'b1 ? Strongly_taken : Strongly_not_taken;
                Weakly_taken: PHT[update_PHT_index] <= actual_takeM == 1'b1 ? Strongly_taken : Strongly_not_taken;
                default: PHT[update_PHT_index] <= Weakly_taken;
            endcase 
        end
    end

    // 最终预测结果
    assign pred_takeD = branchD & pred_takeF_r;
endmodule