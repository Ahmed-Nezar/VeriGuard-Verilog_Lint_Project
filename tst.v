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

module UninitializedRegister(data_out);
    reg data;
    output reg data_out;
    assign data_out = data;
endmodule

module InferringLatches(enable, Data, out);
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

module NonFullCase(y_out);
    output reg [1:0] y_out;
    reg [1:0] x, y;

    always @(*) 
    begin
        case(x)
            2'b00: y = 1'b00;
            2'b01: y = 1'b01;
            // Missing cases for '10' & '11'
        endcase
        y_out = y;
    end
endmodule

module NonParallelCase(y_out);
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

module MultipleDrivers(input [1:0] x, output out);
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

module ArithmeticOverflow(a,b,result);
    input reg [3:0] a, b;
    output reg [3:0] result;
    
    assign result = a + b;
endmodule

module FeedbackLoopExample(clk, rst, data_out);
    input clk, rst;
    output reg data_out;
    reg [3:0] counter;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            counter <= 4'b0000;
            data_out <= 1'b0;
        end else begin
            counter <= counter + 1;
            data_out <= counter[0];
        end
    end
endmodule