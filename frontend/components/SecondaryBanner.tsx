import Image from "next/image";
import React from "react";

interface BannerProps {
  message: string;
}

function SecondaryBanner({ message }: BannerProps) {
  return (
    <div className="absolute inset-0  ">
      <Image
        src="https://img.freepik.com/free-psd/3d-circular-beige-base-placing-objects_125540-1325.jpg?w=1950&t=st=1661982626~exp=1661983226~hmac=53f9cf235deb10d588c48d05443ea79d8c7ca90935a3e1aead4228a2592632cb"
        layout="fill"
        className="object-fit"
        alt="banner image"
      />
      <div className="absolute inset-0 opacity-70 bg-black bg-blend-lighten" />
    </div>
  );
}

export default SecondaryBanner;
