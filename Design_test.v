module combined_violations();
  // Unreachable Blocks
    always @ (state) begin
        if (state == 2'b00) begin
            data <= 1'b0;
        end else if (state == 2'b10) begin
            data <= 1'b1;
        end else if (state == 2'b11) begin
        end
    end

endmodule
