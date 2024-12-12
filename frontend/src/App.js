import React, { useState } from "react";
import axios from "axios";
import {
  Container,
  Box,
  Typography,
  Paper,
  CircularProgress,
} from "@mui/material";
import { ScrapingForm } from "./components/ScrapingForm";
import { ResultView } from "./components/ResultView";
import "./App.css";

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSubmit = async (productNumber) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(
        "http://localhost:8000/api/scrape/ggook",
        {
          productNo: productNumber,
        },
      );
      setResult(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail
        ? typeof err.response.data.detail === "string"
          ? err.response.data.detail
          : JSON.stringify(err.response.data.detail)
        : "상품 정보 조회 중 오류가 발생했습니다.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          웹 폼 데이터 스크래퍼
        </Typography>

        <ScrapingForm
          onSubmit={handleSubmit}
          loading={loading}
          setError={setError}
          setResult={setResult}
        />

        {loading && (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Paper sx={{ p: 2, mt: 2, bgcolor: "#fff3f3" }}>
            <Typography color="error">
              {typeof error === "string" ? error : JSON.stringify(error)}
            </Typography>
          </Paper>
        )}

        {result && <ResultView data={result} />}
      </Box>
    </Container>
  );
}

export default App;
