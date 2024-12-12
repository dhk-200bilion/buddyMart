import React, { useState } from "react";
import axios from "axios";
import { Container, Paper, Typography, Box } from "@mui/material";
import { ScrapingForm } from "./ScrapingForm";
import { ResultView } from "./ResultView";

function ProductInfo() {
  const [scrapingResult, setScrapingResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleScrape = async (productNumber) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/scrape?productNumber=${encodeURIComponent(
          productNumber,
        )}`,
      );
      setScrapingResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "상품 정보 조회 중 오류가 발생했습니다.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <ScrapingForm onSubmit={handleScrape} loading={loading} />
      {error && (
        <Paper sx={{ p: 2, mt: 2, bgcolor: "#ffebee" }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}
      {scrapingResult && <ResultView data={scrapingResult} />}
    </Container>
  );
}

export default ProductInfo;
