import { useRouter } from "next/router";
import React, { useState } from "react";
import DahbordHeader from "./DahboardHeader";
import { findSupplier } from "../../utils/ApiHandlers";
import SupplierFoundCard from "./supllierSection/SupplierFoundCard";
import axios from "axios";
import Loader from "./Loader";

function FindSupplier() {
  const router = useRouter();
  const [suppliers, setSuppliers] = useState([]);
  const [Partnumber, setPartnumber] = useState("");
  const [Loading, setLoading] = useState(false);
  async function SearchAllSupplier() {
    setLoading(true);
    try {
      setSuppliers([]);
      const response = await axios.get(
        `http://localhost:8000/findsupplier/${Partnumber}`
      );

      const suppliers_from_api = await findSupplier(Partnumber);

      setSuppliers([...response.data, ...suppliers_from_api]);
      setLoading(false);
    } catch (err) {
      setLoading(false);
    }
  }
  return (
    <div>
      <DahbordHeader title="Find The Supplier" />
      <div className="mt-9">
        <button onClick={() => router.push("/dashboard")}>
          <svg
            width="52"
            height="52"
            viewBox="0 0 62 62"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect
              x="0.5"
              y="0.5"
              width="61"
              height="61"
              rx="6.5"
              stroke="#B1B1B1"
            />
            <path
              d="M20 32.5502C18.6667 31.7804 18.6667 29.8559 20 29.0861L29.2727 23.7325C30.6061 22.9627 32.2727 23.925 32.2727 25.4646V36.1718C32.2727 37.7114 30.6061 38.6736 29.2727 37.9038L20 32.5502Z"
              fill="#B1B1B1"
            />
            <path
              d="M34.8182 31H45.0001"
              stroke="#B1B1B1"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
        <div className="flex space-x-9 mt-7">
          <input
            placeholder="Enter SPN Number"
            className="bg-white outline-0 text-[#0E8D90] font-poppins text-lg w-full p-3 rounded-md"
            onChange={(e) => setPartnumber(e.target.value)}
          />
          <button
            className="sidebar-color py-3 px-14 rounded-lg text-white font-poppins text-lg"
            onClick={SearchAllSupplier}
          >
            Search
          </button>
        </div>

        {Loading ? (
          <Loader />
        ) : (
          <>
            {suppliers.length > 0 ? (
              <div className="grid mt-16  grid-cols-1  md:grid-cols-2 lg:grid-cols-3  xl:grid-cols-4 gap-5 container mx-auto">
                {suppliers?.map((supplier, i) => (
                  <SupplierFoundCard
                    key={i}
                    supplierName={supplier}
                    LogoPath={`/logos/${supplier.toLowerCase()}.png`}
                  />
                ))}
              </div>
            ) : suppliers.length == 0 || Partnumber !== "" && (
              <div>No supplier found</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default FindSupplier;
