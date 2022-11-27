module competePred (
    input localpred,
    input globalpred,
    input rst, clk,
    input branchM,
    input actual_takeM,
    input localPred_M,
    input globalPred_M,
    input [31:0] pcD,
    input [31:0] pcM,
    output pred
);
// 定义参数
    parameter Strongly_local = 2'b00, Weakly_local = 2'b01, Weakly_global = 2'b11, Strongly_global = 2'b10;
    parameter CPHT_DEPTH = 5;
    integer i;
// 定义CPHT
    reg [1:0] CPHT [(1 << CPHT_DEPTH) - 1 : 0];

    // 更新CPHT
    assign fail_localPred = localPred_M ^ actual_takeM;
    assign fail_globalPred = globalPred_M ^ actual_takeM;
    assign update_CPHT_index = pcM[CPHT_DEPTH + 2: 2];
    always @(posedge ~clk) begin
        if (rst) begin
            for (i = 0; i < (1<<CPHT_DEPTH); i = i + 1) begin
                CPHT[i] = 0;
            end
        end
        else if (branchM) begin
            case({fail_localPred, fail_globalPred})
                2'b01:                  // 局部预测准确
                    case(CPHT[update_CPHT_index])
                        Strongly_global: CPHT[update_CPHT_index] <= Weakly_global;
                        Weakly_global: CPHT[update_CPHT_index] <= Weakly_local;
                        Weakly_local: CPHT[update_CPHT_index] <= Strongly_local;
                        Strongly_local: CPHT[update_CPHT_index] <= Strongly_local;
                    endcase
                2'b10:                  // 全局预测准确
                    case(CPHT[update_CPHT_index])
                        Strongly_global: CPHT[update_CPHT_index] <= Strongly_global;
                        Weakly_global: CPHT[update_CPHT_index] <= Strongly_global;
                        Weakly_local: CPHT[update_CPHT_index] <= Weakly_global;
                        Strongly_local: CPHT[update_CPHT_index] <= Weakly_local;
                    endcase
                default: CPHT[update_CPHT_index] <=  CPHT[update_CPHT_index]; 
            endcase
        end
    end
    
    // 预测结果
    assign CPHT_index = pcD[CPHT_DEPTH + 2: 2];
    assign isGlobal = CPHT[CPHT_index][1];
    assign pred = isGlobal == 1'b1 ? globalpred : localpred;
endmodule