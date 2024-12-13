import DownloadIcon from "@mui/icons-material/Download";
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  Paper,
  Typography,
  CircularProgress,
} from "@mui/material";
import { saveAs } from "file-saver";
import JSZip from "jszip";
import React, { useState } from "react";
import { ProductDetailView } from "./ProductDetailView";

export function ResultView({ data }) {
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const detailContent = data?.data?.domeggook?.desc?.contents?.item || "";

  const extractImageUrls = (htmlContent) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, "text/html");
    const images = doc.getElementsByTagName("img");
    return Array.from(images)
      .map((img) => img.src)
      .filter((url) => {
        const extension = url.split(".").pop().toLowerCase();
        return ["jpg", "jpeg", "png", "gif"].includes(extension);
      });
  };

  const detailImages = extractImageUrls(detailContent);

  // CORS 체크 함수
  const checkCORS = async (url) => {
    try {
      const response = await fetch(url, { method: "HEAD" });
      return true;
    } catch (error) {
      return false;
    }
  };

  const downloadAllImages = async () => {
    try {
      setIsDownloading(true);
      const zip = new JSZip();
      let successCount = 0;

      for (const [index, url] of detailImages.entries()) {
        try {
          // CORS 체크
          const isCORSEnabled = await checkCORS(url);
          let response;

          if (isCORSEnabled) {
            // CORS가 허용된 경우 직접 다운로드
            response = await fetch(url);
          } else {
            // CORS가 차단된 경우 프록시 사용
            response = await fetch(
              `http://localhost:8000/api/proxy-image?url=${encodeURIComponent(
                url,
              )}`,
            );
          }

          if (!response.ok)
            throw new Error(`HTTP error! status: ${response.status}`);

          const blob = await response.blob();
          const extension = url.split(".").pop().toLowerCase();
          zip.file(`image_${index + 1}.${extension}`, blob);
          successCount++;
        } catch (error) {
          console.error(`이미지 다운로드 실패 (${url}):`, error);
        }
      }

      if (successCount > 0) {
        const content = await zip.generateAsync({ type: "blob" });
        saveAs(content, "product_images.zip");
      } else {
        alert("다운로드할 수 있는 이미지가 없습니다.");
      }
    } catch (error) {
      console.error("ZIP 파일 생성 실패:", error);
      alert("이미지 다운로드 중 오류가 발생했습니다.");
    } finally {
      setIsDownloading(false);
    }
  };

  const DownloadButton = ({ variant = "outlined", color = "primary" }) => (
    <Button
      variant={variant}
      startIcon={
        isDownloading ? <CircularProgress size={20} /> : <DownloadIcon />
      }
      onClick={downloadAllImages}
      color={color}
      disabled={isDownloading}
    >
      {isDownloading ? "다운로드 중..." : "전체 이미지 다운로드"}
    </Button>
  );

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      <ProductDetailView data={data} />

      <Box sx={{ mt: 2, mb: 2 }}>
        <Button
          variant="contained"
          onClick={() => setIsDetailOpen(true)}
          sx={{ mr: 2 }}
        >
          상품 상세정보 보기
        </Button>
        {detailImages.length > 0 && <DownloadButton />}
      </Box>

      <Dialog
        open={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent>
          <Box sx={{ mb: 2, display: "flex", justifyContent: "flex-end" }}>
            {detailImages.length > 0 && <DownloadButton variant="contained" />}
          </Box>
          <Box
            sx={{
              "& img": {
                maxWidth: "100%",
                height: "auto",
                display: "block",
                margin: "10px auto",
              },
            }}
          >
            <div dangerouslySetInnerHTML={{ __html: detailContent }} />
          </Box>
        </DialogContent>
      </Dialog>

      <Box
        sx={{
          mt: 2,
          p: 2,
          backgroundColor: "#f5f5f5",
          borderRadius: 1,
          maxHeight: "400px",
          overflow: "auto",
        }}
      >
        <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      </Box>
    </Paper>
  );
}
