module dynamicBranchPredict (
    input clk,
    input rst,
    input flushD,
    input flushE,
    input stallD,
    input wire [31:0] pcF,
    input branchD,
    input branchM,
    input actual_takeM,
    output pred_takeD
);

    wire [31:0] pcD,pcE,pcM;

    globalPred B(
        clk, 
        rst,
        flushD,
        stallD,
        pcF,
        pcM,
        branchM,         // M阶段是否是分支指令
        actual_takeM,    // 实际是否跳转
        pred_takeM,      // M阶段的指令预测是否跳转
        branchD,        // 译码阶段是否是跳转指令   
        globalPred_D      // 预测是否跳转
    );

    localPred C(
        clk, 
        rst,
        flushD,
        stallD,
        pcF,
        pcM,
        branchM,         // M阶段是否是分支指令
        actual_takeM,    // 实际是否跳转
        branchD,        // 译码阶段是否是跳转指令   
        localPred_D      // 预测是否跳转
    );    
    // IF/ID stage
	flopenrc #(32) pcF_D(clk,rst,~stallD,flushD,pcF,pcD);

    // ID/EX stage
	floprc #(1) localPredD_E(clk,rst,flushE,localPred_D,localPred_E);
	floprc #(1) globalPredD_E(clk,rst,flushE,globalPred_E,globalPred_E);
	floprc #(1) predD_E(clk,rst,flushE,pred_takeD,pred_takeE);
	floprc #(32) pcD_E(clk,rst,flushE,pcD,pcE);

    // EX/MEM stage
	flopr #(32) localPredE_M(clk,rst,localPred_E,localPred_M);
	flopr #(32) globalPredE_M(clk,rst,globalPred_E,globalPred_M);
	flopr #(32) predE_M(clk,rst,pred_takeE,pred_takeM);
	flopr #(32) pcE_M(clk,rst,pcE,pcM);
    
    competePred A(
        localPred_D,
        globalPred_D,
        rst, 
        clk,
        branchM,
        actual_takeM,
        localPred_M,
        globalPred_M,
        pcD,
        pcM,
        pred_takeD
    );
endmodule