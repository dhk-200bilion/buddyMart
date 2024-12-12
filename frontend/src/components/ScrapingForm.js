import React, { useState } from "react";
import { Paper, TextField, Button, Box, CircularProgress } from "@mui/material";

export function ScrapingForm({ onSubmit, loading }) {
  const [productNumber, setProductNumber] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(productNumber);
  };

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: "flex", gap: 2 }}>
          <TextField
            fullWidth
            label="상품번호 입력"
            variant="outlined"
            value={productNumber}
            onChange={(e) => setProductNumber(e.target.value)}
            disabled={loading}
            placeholder="예: 37511752"
          />
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !productNumber}
            sx={{ minWidth: "120px" }}
          >
            {loading ? <CircularProgress size={24} /> : "도매꾹 상품 조회"}
          </Button>
        </Box>
      </form>
    </Paper>
  );
}
