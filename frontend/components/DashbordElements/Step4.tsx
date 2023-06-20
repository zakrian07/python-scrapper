/* eslint-disable react-hooks/rules-of-hooks */
import React, { useState } from "react";
import { useAppSelector, useAppDispatch } from "../../Redux/hooks";
import {
  setSupplier,
  setSupplierType,
  SelectPartnumbers,
  SelectSupplier,
  selectSupplierType,
} from "../../Redux/Slices/StepperSlice";
import GetLiveData from "../../utils/GetLiveData";
import Loader from "./Loader";
import fileDownload from "js-file-download";
import ToastErrorPanel from "../../utils/error-toast";
import WheelProgressBar from "../../utils/progressbar";

var numeral = require("numeral");

function Step4() {
  const dispatch = useAppDispatch();
  const [progressComplete, setProgressComplete] = useState(false);
  const partnumbers: string[] = useAppSelector(SelectPartnumbers);
  const supplierType: string = useAppSelector(selectSupplierType);
  const supplier: string = useAppSelector(SelectSupplier);
  const [downloadableData, setDownloadableData] = useState("");
  const [loading, setLoading] = useState(false);
  const [successData, setSuccessData] = useState(0);
  const [failedData, setFailedData] = useState<any>(null);

  async function Generate() {
    setLoading(true);
    try {
      const response = await GetLiveData({
        type: supplierType,
        supplier,
        partnumbers,
        isCsv: true,
      });
      setProgressComplete(true);
      setTimeout(() => {
        setDownloadableData(response.csv_data);
        setSuccessData(response.LiveData.body.length);
        setFailedData(response.failedData);
        setLoading(false);
        console.log("Delayed function executed");
      }, 3000);
    } catch {
      setProgressComplete(true);
      setTimeout(() => {
        setLoading(false);
        setFailedData(true);
        setSuccessData(0);
      }, 2000);
    }
  }

  const Download = () => {
    if (downloadableData) {
      fileDownload(downloadableData, "Filled_Template.csv");
    }
  };

  const DownloadNot = () => {
    if (failedData) {
      fileDownload(failedData, "NotFound_Template.csv");
    }
  };

  return (
    <div className="bg-gray-200 rounded-lg relative flex flex-col justify-center items-center space-y-3 px-5 py-24 mt-9">
      {downloadableData ? (
        <div className="flex self-center">
          <div className="px-10">
            <button
              className="sidebar-color flex items-center space-x-7 text-white rounded-md font-poppins text-2xl px-16 py-2"
              onClick={Download}
            >
              <svg
                width="30"
                height="35"
                viewBox="0 0 96 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M77.4 24.16C74.68 10.36 62.56 0 48 0C36.44 0 26.4 6.56 21.4 16.16C9.36 17.44 0 27.64 0 40C0 53.24 10.76 64 24 64H76C87.04 64 96 55.04 96 44C96 33.44 87.8 24.88 77.4 24.16ZM68 36L48 56L28 36H40V20H56V36H68Z"
                  fill="white"
                />
              </svg>
              <p>Export Completed template</p>
            </button>
          </div>

          <div className="">
            <p className="text-lg font-bold">
              SPNs uploaded: {numeral(partnumbers.length).format("0,0")}
            </p>
            <p className="text-lg font-bold">
              Found: {numeral(successData).format("0,0")}
            </p>
            <p className="text-lg font-bold">
              Not Found: {numeral(failedData?.length).format("0,0")}
            </p>
            {failedData?.length > 0 && (
              <p className="py-4 text-red-600 flex">
                Not Found List:
                <svg
                  width="30"
                  height="30"
                  viewBox="0 0 96 64"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="mx-4 cursor-pointer"
                  onClick={DownloadNot}
                >
                  <path
                    d="M77.4 24.16C74.68 10.36 62.56 0 48 0C36.44 0 26.4 6.56 21.4 16.16C9.36 17.44 0 27.64 0 40C0 53.24 10.76 64 24 64H76C87.04 64 96 55.04 96 44C96 33.44 87.8 24.88 77.4 24.16ZM68 36L48 56L28 36H40V20H56V36H68Z"
                    fill="red"
                  />
                </svg>
              </p>
            )}

            <div>
              {failedData &&
                failedData?.map((data: any, i: any) => (
                  <p className="ml-4" key={i}>
                    {data.PArtname}
                  </p>
                ))}
            </div>
          </div>
        </div>
      ) : (
        !loading && (
          <>
            <p className="font-semibold text-sm text-black">
              Click to start generating a filled template
            </p>
            <button
              className="bg-green-500  flex items-center space-x-7 text-white rounded-md font-poppins text-2xl px-16 py-2"
              onClick={Generate}
            >
              <p>Fill document out</p>
            </button>
          </>
        )
      )}
      {console.log(loading, failedData, successData, "in test mode -----")}
      {loading && <WheelProgressBar progressCompleted={progressComplete} />}
      {!loading && failedData && !successData && (
        <ToastErrorPanel message="Data not found or temporarily unavailable" />
      )}
    </div>
  );
}

export default Step4;
