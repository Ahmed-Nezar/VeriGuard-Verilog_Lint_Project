module combined_violations();
    wire enable, Data;
    reg out;
    reg [1:0] state;

  // Unreachable Blocks
    always @ (state) 
    begin
        if (state == 2'b00) 
        begin
            data <= 1'b0;
        end 
        else if (state == 2'b10) 
        begin
            data <= 1'b1;
        end 
        else if (state == 2'b11) 
        begin

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

endmodule
