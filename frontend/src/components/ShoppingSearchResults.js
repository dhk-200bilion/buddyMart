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
import React, { useState } from "react";

export function ShoppingSearchResults({ productTitle }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchProducts = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.post(
        "http://localhost:8000/api/search/shopping",
        {
          keyword: productTitle,
        }
      );

      setResults(response.data.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "상품 검색 중 오류가 발생했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ mt: 3 }}>
      <Button
        variant="contained"
        onClick={searchProducts}
        disabled={loading}
        sx={{ mb: 2 }}
      >
        네이버 쇼핑 검색
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
          {results.items.map((item, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardMedia
                  component="img"
                  height="200"
                  image={item.image}
                  alt={item.title}
                  sx={{ objectFit: "contain" }}
                />
                <CardContent>
                  <Typography
                    gutterBottom
                    variant="h6"
                    component="div"
                    dangerouslySetInnerHTML={{ __html: item.title }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    최저가: {parseInt(item.lprice).toLocaleString()}원
                  </Typography>
                  {item.hprice && (
                    <Typography variant="body2" color="text.secondary">
                      최고가: {parseInt(item.hprice).toLocaleString()}원
                    </Typography>
                  )}
                  <Typography variant="body2" color="text.secondary">
                    판매처: {item.mallName}
                  </Typography>
                  <Button
                    variant="outlined"
                    href={item.link}
                    target="_blank"
                    sx={{ mt: 1 }}
                  >
                    상품 보기
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
