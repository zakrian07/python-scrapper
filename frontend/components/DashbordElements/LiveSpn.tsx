import { useRouter } from "next/router";
import React, { useState } from "react";
import DahbordHeader from "./DahboardHeader";
import suppliersList from "../../utils/suppliers";
import GetLiveData from "../../utils/GetLiveData";
import Loader from "./Loader";
import DataTable from "./DataTable";
import ToastErrorPanel from "../../utils/error-toast";

function LiveSpn() {
  const router = useRouter();
  const [supplier, setsupplier] = useState("");
  const [type, settype] = useState("supplier");
  const [SearchInput, setSearchInput] = useState("");
  const [PreviousSearchInput, setPreviousSearchInput] = useState("");
  const [Loading, setLoading] = useState(false);
  const [showError, setShowError] = useState(false);
  const [LiveData, setLiveData] = useState<any>("");

  async function SearchLiveData() {
    if (!SearchInput || !type || !supplier) return;
    try {
      // if (PreviousSearchInput == SearchInput) return;
      setLoading(true);
      setLiveData(null);
      console.log("in error message ---------")
      let partnumbers = SearchInput.split(",");
      setPreviousSearchInput(SearchInput);
      partnumbers = partnumbers.filter(
        (item, index) => partnumbers.indexOf(item) === index
      );

      const response = await GetLiveData({
        type,
        supplier,
        partnumbers,
      });
      console.log(response);
      setLiveData(response?.LiveData || "");
      setLoading(false);
    } catch (e) {
      console.log("------ error handling of catch-----")
      setShowError(true);
      setLiveData(null)
      setLoading(false);
    }
  }
  return (
    <div>
      <DahbordHeader title="Live Spn Data" />
      <div className={`mt-9 flex flex-col `}>
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
        <div className="flex mt-6 space-x-7">
          <select
            onChange={(e) => settype(e.target.value == "" ? "supplier" : e.target.value)}
            name="Type of supplier"
            className="w-full  my-2 smooth-transition min-h-[50px] rounded-lg font-poppins text-lg cursor-pointer hover:shadow-lg shadow-md border-0"
          >
            <option value="">Type of supplier</option>

            <option value="Manufacturer">Manufacturer</option>
            <option value="Distributer">Distributer</option>
          </select>

          <select
            onChange={(e) => {
              setsupplier(e.target.value);
            }}
            name="supplier"
            className="w-full mx-5 my-2 smooth-transition min-h-[50px]  rounded-lg font-poppins text-lg cursor-pointer hover:shadow-lg shadow-md border-0"
          >
            <option value="">Select {type}</option>
            {type == "Manufacturer"
              ? suppliersList.manufacturers.map((manufacturer, i) => (
                <option key={i} value={manufacturer}>
                  {manufacturer}
                </option>
              ))
              : suppliersList.distributers.map((distributer, i) => (
                <option key={i} value={distributer}>
                  {distributer}
                </option>
              ))}
          </select>
        </div>

        <div className={`flex space-x-9 mt-7`}>
          <input
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Enter SPN Number"
            className="bg-white outline-0 text-[#0E8D90] font-poppins text-lg flex flex-1  p-3 rounded-md"
          />
          <button
            className="sidebar-color py-3 px-14 rounded-lg text-white font-poppins text-lg"
            onClick={SearchLiveData}
          >
            Search
          </button>
        </div>
        <div className="relative mt-16 min-h-[500px]  w-full">
          {Loading && <Loader />}
          {!Loading && !LiveData && showError && <ToastErrorPanel message="Data not found or temporarily unavailable" />}
          {LiveData && (
            <DataTable head={LiveData?.head} body={LiveData?.body} />
          )}
        </div>
      </div>

    </div >
  );
}

export default LiveSpn;
