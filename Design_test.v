module combined_violations();
    wire enable, Data;
    reg out;
    reg [1:0] state;
    reg y;
    input clk;
    localparam [1:0] S1 = 2'b00 ;
    localparam [1:0] S2 = 2'b01 ;
    localparam [1:0] S3 = 2'b10 ;
    reg [1:0] current_state;
    reg [1:0] next_state;

  // Unreachable Blocks
    y = 1'b1;
    always @ (state) 
    begin
        if (y == 2'b0) 
        begin
            data <= 1'b1;
        end 
    end

        // Un-initialized Register
    initial 
    begin
        $display("%b", data); 
    end
    

    //inferring latches
    always @ (enable) 
    begin
        if (enable) 
        begin
            out <= Data;
        end
    end
    //unreachable State
    always @(posedge clk) begin
        current_state <= next_state;
    end
    always @(*) begin
        case (current_state)
            S1: begin
                next_state <= S2;
            end
            S2: begin
                next_state <= S1;
            end
            S3: begin
                next_state <= S1;
            end
        endcase
    end
    


endmodule
