import React from "react";

interface pageProps {
  logo: string;
  quantity: number;
}

function SupplierInfo({ logo, quantity }: pageProps) {
  return (
    <div className="flex flex-shrink items-center justify-between my-5">
      <div className="flex items-center">
        <img src={`${logo}`} className="w-12 h-12" />
        <p className="text-2xl font-semibold pl-4">RX</p>
      </div>
      <div className="flex items-center">
        <p className="text-xl font-thin text-gray-500 px-2">sold</p>
        <p className="text-2xl font-semibold px-2">{quantity}</p>
      </div>
    </div>
  );
}

export default SupplierInfo;
