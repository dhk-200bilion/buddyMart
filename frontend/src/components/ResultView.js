import React from "react";
import { Paper, Typography, Box, Button } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Image";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

export function ResultView({ data }) {
  const handleImageDownloadPage = () => {
    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>상품 상세 정보</title>
          <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
          <style>
            body {
              font-family: Arial, sans-serif;
              max-width: 1200px;
              margin: 0 auto;
              padding: 20px;
              background-color: #f5f5f5;
            }
            .content-container {
              background: white;
              padding: 20px;
              border-radius: 8px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .image-container {
              max-width: 800px;
              margin: 20px auto;
            }
            img {
              max-width: 100%;
              height: auto;
              margin: 10px 0;
              border-radius: 4px;
            }
            .button-container {
              margin: 20px 0;
              text-align: center;
            }
            button {
              padding: 10px 20px;
              margin: 0 10px;
              border: none;
              border-radius: 4px;
              background-color: #1976d2;
              color: white;
              cursor: pointer;
            }
            button:hover {
              background-color: #1565c0;
            }
            .slider-container {
              width: 100%;
              max-width: 800px;
              margin: 0 auto;
            }
            .slider-image {
              width: 100%;
              height: auto;
              object-fit: contain;
            }
          </style>
        </head>
        <body>
          <div class="content-container">
            <h2>이미지 갤러리</h2>
            <div class="slider-container">
              <div class="image-container">
                ${Array.from(data.images || [])
                  .map(
                    (image) => `
                    <img src="${image}" alt="Product" class="slider-image" />
                  `,
                  )
                  .join("")}
              </div>
            </div>
            <div class="button-container">
              <button onclick="downloadAllImages()">모든 이미지 다운로드</button>
              <button onclick="downloadAsZip()">ZIP으로 다운로드</button>
            </div>
          </div>

          <script>
            async function downloadAllImages() {
              const images = document.getElementsByTagName('img');
              let index = 0;
              
              for (const img of images) {
                try {
                  const response = await fetch(img.src);
                  const blob = await response.blob();
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'image_' + (index + 1) + '.png';
                  document.body.appendChild(a);
                  a.click();
                  window.URL.revokeObjectURL(url);
                  document.body.removeChild(a);
                  index++;
                } catch (error) {
                  console.error('이미지 다운로드 실패:', error);
                }
              }
              alert('모든 이미지 다운로드가 완료되었습니다!');
            }

            async function downloadAsZip() {
              const zip = new JSZip();
              const images = document.getElementsByTagName('img');
              let index = 0;
              
              try {
                for (const img of images) {
                  const response = await fetch(img.src);
                  const blob = await response.blob();
                  zip.file('image_' + (index + 1) + '.png', blob);
                  index++;
                }
                
                const content = await zip.generateAsync({type: 'blob'});
                const url = window.URL.createObjectURL(content);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'images.zip';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                alert('ZIP 파일 다운로드가 완료되었습니다!');
              } catch (error) {
                console.error('ZIP 파일 생성 실패:', error);
                alert('ZIP 파일 생성 중 오류가 발생했습니다.');
              }
            }
          </script>
        </body>
      </html>
    `;

    const newWindow = window.open();
    newWindow.document.write(htmlContent);
    newWindow.document.close();
  };

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    adaptiveHeight: true,
    arrows: true,
    autoplay: false,
  };

  console.log("Images data:", data.images);

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">스크래핑 결과</Typography>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={handleImageDownloadPage}
        >
          상세 정보 보기
        </Button>
      </Box>

      {data.html && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: "bold", mb: 2 }}>
            이미지 미리보기
          </Typography>
          <Box
            sx={{
              maxWidth: "800px",
              margin: "0 auto",
              "& .slick-prev, & .slick-next": {
                zIndex: 1,
                "&:before": {
                  color: "#000",
                },
              },
              "& .slick-prev": { left: 10 },
              "& .slick-next": { right: 10 },
            }}
          >
            <Slider {...sliderSettings}>
              {Array.from(
                new DOMParser()
                  .parseFromString(data.html, "text/html")
                  .querySelectorAll("img"),
              ).map((img, index) => (
                <div key={index}>
                  <img
                    src={img.src}
                    alt={`Product ${index + 1}`}
                    style={{
                      width: "100%",
                      height: "auto",
                      objectFit: "contain",
                      maxHeight: "500px",
                    }}
                  />
                </div>
              ))}
            </Slider>
          </Box>
        </Box>
      )}

      <Typography variant="subtitle1" sx={{ fontWeight: "bold", mt: 2 }}>
        스크래핑 URL
      </Typography>
      <Typography>{data.url}</Typography>

      <Typography variant="subtitle1" sx={{ fontWeight: "bold", mt: 2 }}>
        스크래핑 데이터
      </Typography>
      <Box
        sx={{
          mt: 1,
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
