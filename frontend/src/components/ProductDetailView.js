import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DownloadIcon from "@mui/icons-material/Download";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import PriceCheckIcon from "@mui/icons-material/PriceCheck";
import VerifiedIcon from "@mui/icons-material/Verified";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  Snackbar,
  Typography,
} from "@mui/material";
import { saveAs } from "file-saver";
import React, { useEffect, useState } from "react";
import { CoupangSearchResults } from "./CoupangSearchResults";

export function ProductDetailView({ data }) {
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [resetCoupangSearch, setResetCoupangSearch] = useState(0);
  const product = data?.data?.domeggook;

  useEffect(() => {
    setResetCoupangSearch((prev) => prev + 1);
  }, [data]);

  if (!product) return null;

  const copyKeywords = async () => {
    const keywordText = product.basis.keywords.kw.join(",");
    try {
      await navigator.clipboard.writeText(keywordText);
      setOpenSnackbar(true);
    } catch (err) {
      console.error("키워드 복사 실패:", err);
      alert("키워드 복사 중 오류가 발생했습니다.");
    }
  };

  const downloadThumbnail = async (url, filename) => {
    try {
      const proxyUrl = `http://localhost:8000/api/proxy-image?url=${encodeURIComponent(
        url
      )}`;
      const response = await fetch(proxyUrl);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      saveAs(blob, filename);
    } catch (error) {
      console.error("썸네일 다운로드 실패:", error);
      alert("썸네일 다운로드 중 오류가 발생했습니다.");
    }
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        {/* 상품 기본 정보 */}
        <Grid container spacing={3}>
          {/* 썸네일 이미지 */}
          <Grid item xs={12} md={4}>
            <Box sx={{ position: "relative" }}>
              <img
                src={product.thumb.large}
                alt={product.basis.title}
                style={{ width: "100%", height: "auto" }}
              />
              <Box sx={{ mt: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  size="small"
                  onClick={() =>
                    downloadThumbnail(
                      product.thumb.original,
                      `thumbnail_${product.basis.no}.jpg`
                    )
                  }
                >
                  원본 이미지 다운로드
                </Button>
              </Box>
            </Box>
          </Grid>

          {/* 상품 정보 */}
          <Grid item xs={12} md={8}>
            <Typography variant="h5" gutterBottom>
              {product.basis.title}
            </Typography>

            {/* 키워드 */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Typography variant="subtitle1" sx={{ flex: 1 }}>
                  키워드
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<ContentCopyIcon />}
                  onClick={copyKeywords}
                >
                  키워드 복사
                </Button>
              </Box>
              <Box>
                {product.basis.keywords.kw.map((keyword, index) => (
                  <Chip
                    key={index}
                    label={keyword}
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                  />
                ))}
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            {/* 가격 정보 */}
            <Box sx={{ mb: 2 }}>
              <Typography
                variant="subtitle1"
                sx={{ display: "flex", alignItems: "center", mb: 1 }}
              >
                <PriceCheckIcon sx={{ mr: 1 }} /> 가격 정보
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    도매가
                  </Typography>
                  <Typography variant="h6">
                    {Number(product.price.dome).toLocaleString()}원
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    공급가
                  </Typography>
                  <Typography variant="h6">
                    {Number(product.price.supply).toLocaleString()}원
                  </Typography>
                </Grid>
              </Grid>
            </Box>

            {/* 배송 정보 */}
            <Box sx={{ mb: 2 }}>
              <Typography
                variant="subtitle1"
                sx={{ display: "flex", alignItems: "center", mb: 1 }}
              >
                <LocalShippingIcon sx={{ mr: 1 }} /> 배송 정보
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    배송방법: {product.deli.method}
                  </Typography>
                  <Typography variant="body2">
                    배송비: {Number(product.deli.dome.fee).toLocaleString()}원
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    결제방식: {product.deli.pay}
                  </Typography>
                  <Typography variant="body2">
                    평균배송일: {product.deli.sendAvg}일
                  </Typography>
                </Grid>
              </Grid>
            </Box>

            {/* 라이선스 및 과세 정보 */}
            <Box>
              <Typography
                variant="subtitle1"
                sx={{ display: "flex", alignItems: "center", mb: 1 }}
              >
                <VerifiedIcon sx={{ mr: 1 }} /> 추가 정보
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    이미지 라이선스:{" "}
                    {product.desc.license.usable === "true"
                      ? "사용 가능"
                      : "사용 불가"}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    과세 여부: {product.basis.tax}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </Grid>
        </Grid>

        {/* 쿠팡 검색 결과 추가 */}
        <CoupangSearchResults
          productTitle={product.basis.title}
          key={resetCoupangSearch}
        />
      </CardContent>

      {/* 복사 완료 알림 */}
      <Snackbar
        open={openSnackbar}
        autoHideDuration={2000}
        onClose={() => setOpenSnackbar(false)}
        message="키워드가 클립보드에 복사되었습니다"
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </Card>
  );
}
