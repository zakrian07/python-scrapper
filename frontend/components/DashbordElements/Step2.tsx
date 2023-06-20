import React, { useState } from "react";
import readXlsxFile from "read-excel-file";
import Papa from "papaparse";
import { useAppSelector, useAppDispatch } from "../../Redux/hooks";
import { SetParnumbers } from "../../Redux/Slices/StepperSlice";

interface stepProps {
  nextStep: () => void;
}

function Step2({ nextStep }: stepProps) {
  const dispatch = useAppDispatch();

  const AddPartnumbersToRedux = (partnumbers: string[]) => {
    dispatch(SetParnumbers(partnumbers));
  };
  const [isUploaded, setIsUploaded] = useState(false);
  async function UploadTemplate(e: React.ChangeEvent<HTMLInputElement>) {
    if (e === null) return;
    try {
      if (e?.target?.files[0].name.includes(".xlsx")) {
        readXlsxFile(e?.target?.files[0]).then((rows) => {
          AddPartnumbersToRedux(
            rows
              .splice(1)
              .filter((row) => Number(row[0]) !== NaN && row[0] !== "")
              .map((row) => `${row[0]}`)
          );
        });
      } else {
        Papa.parse(e?.target?.files[0], {
          complete: ({ data }) => console.log(data[0]),
        });
      }

      setIsUploaded(true);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <>
      <div className="bg-gray-200 rounded-lg space-y-3 px-5 py-9 mt-9 border flex flex-col justify-center items-center  border-dashed border-gray-500">
        <svg
          width="60"
          height="60"
          viewBox="0 0 60 60"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M44.0625 41.25H43.125V37.5H44.0625C46.3002 37.5896 48.4819 36.7865 50.1275 35.2674C51.7732 33.7484 52.748 31.6378 52.8375 29.4001C52.927 27.1623 52.1239 24.9806 50.6048 23.335C49.0858 21.6894 46.9752 20.7146 44.7375 20.625H43.125L42.9375 19.0876C42.5215 15.9309 40.9722 13.0331 38.5783 10.9339C36.1843 8.83472 33.1089 7.67733 29.925 7.67733C26.741 7.67733 23.6656 8.83472 21.2717 10.9339C18.8777 13.0331 17.3285 15.9309 16.9125 19.0876L16.875 20.625H15.2625C13.0247 20.7146 10.9142 21.6894 9.39512 23.335C7.87607 24.9806 7.07297 27.1623 7.16248 29.4001C7.25199 31.6378 8.22678 33.7484 9.87241 35.2674C11.518 36.7865 13.6997 37.5896 15.9375 37.5H16.875V41.25H15.9375C12.9307 41.231 10.0372 40.1012 7.81308 38.0777C5.58899 36.0543 4.19139 33.2801 3.88897 30.2886C3.58656 27.297 4.40069 24.2993 6.17483 21.8717C7.94897 19.444 10.5579 17.758 13.5 17.1376C14.3094 13.3623 16.389 9.97875 19.3918 7.55155C22.3946 5.12436 26.1389 3.80029 30 3.80029C33.8611 3.80029 37.6054 5.12436 40.6081 7.55155C43.6109 9.97875 45.6905 13.3623 46.5 17.1376C49.4421 17.758 52.051 19.444 53.8251 21.8717C55.5993 24.2993 56.4134 27.297 56.111 30.2886C55.8086 33.2801 54.411 36.0543 52.1869 38.0777C49.9628 40.1012 47.0692 41.231 44.0625 41.25V41.25Z"
            fill="#0E8D90"
          />
          <path
            d="M31.875 33.4312V56.25H28.125V33.4312L23.2687 38.2687L20.625 35.625L30 26.25L39.375 35.625L36.7313 38.2687L31.875 33.4312Z"
            fill="#0E8D90"
          />
        </svg>

        <input
          id="inputFile"
          type="file"
          accept={".csv,.xlsx"}
          className="hidden"
          onChange={(e) => UploadTemplate(e)}
        />
        <label
          htmlFor="inputFile"
          className={`flex   justify-center rounded-lg   cursor-pointer`}
        >
          <div
            className={` ${isUploaded ? "bg-green-600" : "sidebar-color"
              } text-white  font-poppins px-9 py-3 rounded-lg `}
          >
            {isUploaded ? "Succesfully uploaded" : "Upload File"}
          </div>
        </label>
      </div>
      {isUploaded && (
        <div className="flex justify-center items-center mt-7">
          <button
            disabled={false}
            className={`border border-gray-400   sidebar-color text-white
             rounded-lg  font-poppins text-lg px-16 py-2`}
            onClick={nextStep}
          >
            Continue
          </button>
        </div>
      )}
    </>
  );
}

export default Step2;
