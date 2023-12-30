module Edge_Cases (A); // No Violations
input reg A;
always @(*) 
begin
    case (A):
        1'b0: A = 1'b1;
        1'b1: A = 1'b0;
    endcase
end
    
endmodule

module Vector_Input (A); // Non-Full case
input reg [1:0] A;
always @(*)
 begin
    case (A):
        1'b0: A = 1'b1;
        1'b1: A = 1'b0;
    endcase
end
    
endmodule

module CaseZ_Parallel_Case (A); // No violations
input reg [3:0] A;
always @(*)
begin
    casez (A): // synopsys full_case parallel_case
        4'b???1: F = 2'b00;
        4'b??1?: F = 2'b01;
        4'b?1??: F = 2'b10;
        4'bl???: F = 2'b11;
    endcase
end
    
endmodule

module Sequential_Case (t); // No Violations
input reg [3:0] t;
always @(*)
begin
    case (t): // synopsys full_case
        4'b0000: t = 4'b0001;
        4'b0001: t = 4'b0010;
    endcase
end
endmodule

module UnreachableBlocks(data_out);
    output reg data_out;
    reg reach;
    wire state;

    initial 
    begin
        reach = 1'b1;
    end

    always @(state) 
    begin
        if (reach == 2'b0) 
        begin
            data_out = 1'b1;
        end 
        else 
        begin
            data_out = 1'b0;
        end
    end
endmodule

module UninitializedRegister(data_out); // Uninitialized register error
    reg data;
    output reg data_out;
    assign data_out = data;
endmodule

module InferringLatches(enable, Data, out); // inferring latches error
    input wire enable, Data
    output reg out;

    always @(enable) 
    begin
        if (enable) 
        begin
            out = Data;
        end
    end
endmodule

module UnreachableState(clk, state_out); 
    input clk;
    output reg [1:0] state_out;
    reg [1:0] current_state, next_state;
    localparam [1:0] S1 = 2'b00 ;
    localparam [1:0] S2 = 2'b01 ;
    localparam [1:0] S3 = 2'b10 ;

    always @(posedge clk) 
    begin
        current_state <= next_state;
    end

    always @(*) 
    begin
        case (current_state)
            S1: 
            begin
            next_state <= S2;
            end
            S2: 
            begin
                next_state <= S1;
            end
            S3:
            begin
                next_state <= S1;
            end
        endcase
        state_out = current_state;

    end
endmodule

module Incomplete_Case (y_out); // non-full_case
    output reg [1:0] y_out;
    reg [1:0] x, y;

    always @(*) 
    begin
        case(x):
            2'b00: y = 1'b00;
            2'b01: y = 1'b01;
            // Missing cases for '10' & '11'
        endcase
        y_out = y;
    end
endmodule

module NonParallelZ (x); // non-parallel_case
    input [1:0] x;
    reg [1:0] y;
    always @(*)
    begin
        casez (x)
            2'b??: y = 1'b00;
            2'b??: y = 1'b01;
            2'b??: y = 1'b10;
            2'b??: y = 1'b11;
        endcase
    end
endmodule

module NonParallelX (x); // non-parallel_case
    input [1:0] x;
    reg [1:0] y;
    always @(*)
    begin
        casex (x)
            2'bxx: y = 1'b00;
            2'bxx: y = 1'b01;
            2'bxx: y = 1'b10;
            2'bxx: y = 1'b11;
        endcase
    end
endmodule

module Full_Case (y_out); // full_case
    output reg [1:0] y_out;
    reg [1:0] x, y;

    always @(*) 
    begin
        case(x)
            2'b00: y = 1'b00;
            2'b0?: y = 1'b01;
            2'b?0: y = 1'b10;
            default: y = 1'b11;
        endcase
        y_out = y;
    end
endmodule

module MultipleDrivers(input [1:0] x, output out); // Multiple Drivers error
    input [1:0] myIn;
    reg y;
    
    // In the 2 following lines, out is multdriven by two assign statements
    assign out = x;
    assign out = 0'b1;

    // In the 2 following always blocks, y is multidriven
    always @(*)
    begin
        y = y + 1;
    end
    always @(*)
    begin
        y = 1'b0;
    end
endmodule

module MultipleDrivers2 (input [1:0] x, output out2); // Multiple Drivers error
    input [1:0] myIn;
    

    assign out2 = 0'b1;

    // In the 2 following always blocks, y is multidriven
    always @(*)
    begin
        out2 = myIn[0];
    end
    
endmodule

module ArithmeticOverflow(a,b,result); // overflow error when doing operation
    input reg [3:0] a, b;
    output reg [3:0] result = 0;
    
    assign result = a + b;
endmodule

module CombinationalFeedbackLoop(a, b); // Combinational feedback loop error that infer latches
    input a;
    reg b;

    always @(*) 
    begin
    b = b + a; 
    end
endmodule