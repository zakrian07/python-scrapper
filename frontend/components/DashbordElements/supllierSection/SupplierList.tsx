import React from "react";
import SupplierInfo from "./SupplierInfo";

// interface supplierProps {
//   logo: string;
//   quantity: number;
// }
interface pageProps {
  title: string;
  suppliers: any[];
}

function SupplierList({ title, suppliers }: pageProps) {
  return (
    <div className="rounded-lg p-9 bg-white">
      <h1 className="text-3xl text-[#225373] font-semibold mb-10">{title}</h1>
      {suppliers?.map((supplier, i) => (
        <SupplierInfo
          key={i}
          logo={supplier.logo}
          quantity={supplier.quantity}
        />
      ))}
    </div>
  );
}

export default SupplierList;
