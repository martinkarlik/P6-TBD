import React, { useState } from "react";
import ImageCard from "./ImageCard";

export default function Cluster(props) {
  const [numberOfSelectedImages, setNumberOfSelectedImages] = useState(0);

  const imageCards = props.imageBlobArr.map((blob) => {
    return (
      <ImageCard
        key={blob}
        blob={blob[0]}
        setNumberOfSelectedImages={setNumberOfSelectedImages}
      />
    );
  });

  return (
    <div
      className="d-flex flex-column m-2 scrollMenuVertical"
      style={{ alignItems: "center", justifyContent: "center" }}
    >
      {/* Vertical Image Div */}
      <div
        style={{
          backgroundColor: "grey",
          borderRadius: "0px 3px 3px 3px",
        }}
      >
        {/* Creates all the image cards */}
        {imageCards}
      </div>
    </div>
  );
}
