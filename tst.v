module UnreachableBlocks();
    reg reach;
    wire state;
    wire data;

    initial 
    begin
        reach = 1'b1;
    end

    always @(state) 
    begin
        if (reach == 2'b0) 
        begin
            data <= 1'b1;
        end 
    end
endmodule

module UninitializedRegister();
    wire data;

    initial 
    begin
        $display("%b", data); 
    end
endmodule

module InferringLatches();
    reg out;
    wire enable, Data;

    always @(enable) 
    begin
        if (enable) 
        begin
            out <= Data;
        end
    end
endmodule

module UnreachableState(input clk);
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
            S3
            begin
                next_state <= S1;
            end

        endcase
    end
endmodule

module NonFullCase();
    reg [1:0] x, y;

    always @(*) 
    begin
        case(x)
            2'b00: y = 1'b00;
            2'b01: y = 1'b01;
            // Missing cases for '10' & '11'
        endcase
    end
endmodule

module NonParallelCase();
    reg [1:0] x, y;

    always @(*) 
    begin
        case(x)
            2'b00: y = 1'b00;
            2'b0?: y = 1'b01;
            2'b?0: y = 1'b10;
            default: y = 1'b11;
        endcase
    end
endmodule

module MultipleDrivers(input [1:0] myIn);
    wire myOut;
    reg myReg;

    assign myOut = myIn;
    assign myOut = 1'b1;

    always @(*) 
    begin
        myReg = myReg + 1;
    end
    always @(*)
    begin
        myReg = 1'b0;
    end
endmodule

module ArithmeticOverflow();
    reg [3:0] a, b, result;

    always @(*) 
    begin
        result = a + b; // Potential overflow when adding 'a' and 'b'
    end
endmodule