import DownloadIcon from "@mui/icons-material/Download";
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  Paper,
  Typography,
} from "@mui/material";
import { saveAs } from "file-saver";
import JSZip from "jszip";
import React, { useState } from "react";

export function ResultView({ data }) {
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  // 상품 상세 HTML 컨텐츠 가져오기
  const detailContent = data?.data?.domeggook?.desc?.contents?.item || "";

  // 이미지 URL 추출
  const extractImageUrls = (htmlContent) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, "text/html");
    const images = doc.getElementsByTagName("img");
    return Array.from(images).map((img) => img.src);
  };

  const detailImages = extractImageUrls(detailContent);

  const downloadImage = async (url, filename) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      saveAs(blob, filename);
    } catch (error) {
      console.error("이미지 다운로드 실패:", error);
    }
  };

  const downloadAllImages = async () => {
    try {
      const zip = new JSZip();

      const downloads = detailImages.map(async (url, index) => {
        try {
          const response = await fetch(url);
          const blob = await response.blob();
          zip.file(`image_${index + 1}.jpg`, blob);
        } catch (error) {
          console.error(`이미지 다운로드 실패 (${url}):`, error);
        }
      });

      await Promise.all(downloads);
      const content = await zip.generateAsync({ type: "blob" });
      saveAs(content, "product_images.zip");
    } catch (error) {
      console.error("ZIP 파일 생성 실패:", error);
    }
  };

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      {/* 기본 정보 표시 */}
      <Typography variant="h6" gutterBottom>
        상품 정보
      </Typography>

      {/* 상품 상세정보 버튼 */}
      <Box sx={{ mt: 2, mb: 2 }}>
        <Button
          variant="contained"
          onClick={() => setIsDetailOpen(true)}
          sx={{ mr: 2 }}
        >
          상품 상세정보 보기
        </Button>
        {detailImages.length > 0 && (
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={downloadAllImages}
          >
            전체 이미지 다운로드
          </Button>
        )}
      </Box>

      {/* 상세정보 다이얼로그 */}
      <Dialog
        open={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent>
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

      {/* 기존의 JSON 데이터 표시 */}
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
