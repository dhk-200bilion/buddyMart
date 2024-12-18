import {
  Box,
  Button,
  Card,
  CardContent,
  CardMedia,
  CircularProgress,
  Grid,
  Typography,
} from "@mui/material";
import axios from "axios";
import React, { useEffect, useState } from "react";

export function CoupangSearchResults({ productTitle }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchCoupang = async () => {
    try {
      setResults(null);
      setLoading(true);
      setError(null);

      // 최대 3번 재시도
      let retryCount = 0;
      const maxRetries = 3;

      while (retryCount < maxRetries) {
        try {
          const response = await axios.post(
            "http://localhost:8000/api/search/coupang",
            {
              keyword: productTitle,
            },
            {
              timeout: 30000, // 30초로 조정
              headers: {
                "Content-Type": "application/json",
              },
            }
          );

          if (response.data?.data?.products?.length > 0) {
            setResults(response.data.data);
            break;
          } else {
            setError("검색 결과가 없습니다.");
            break;
          }
        } catch (err) {
          retryCount++;
          if (retryCount === maxRetries) {
            throw err;
          }
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }
      }
    } catch (err) {
      console.error("쿠팡 검색 오류:", err);
      setError(
        err.response?.data?.detail ||
          "쿠팡 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      setResults(null);
      setError(null);
    };
  }, []);

  return (
    <Box sx={{ mt: 3 }}>
      <Button
        variant="contained"
        onClick={searchCoupang}
        disabled={loading}
        sx={{ mb: 2 }}
      >
        쿠팡에서 검색
      </Button>

      {loading && (
        <Box display="flex" justifyContent="center" my={2}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {results && (
        <Grid container spacing={2}>
          {results.products.map((product, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                {product.image && (
                  <CardMedia
                    component="img"
                    height="200"
                    image={product.image}
                    alt={product.title}
                    sx={{ objectFit: "contain" }}
                  />
                )}
                <CardContent>
                  <Typography gutterBottom variant="h6" component="div">
                    {product.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    가격: {product.price}원
                  </Typography>
                  <Button
                    variant="outlined"
                    href={product.link}
                    target="_blank"
                    sx={{ mt: 1 }}
                  >
                    쿠팡에서 보기
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
