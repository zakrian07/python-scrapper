import React from "react";

interface StepperProps {
  step: number;
  HandleStep: (value: number) => void;
}
function Stepper({ step, HandleStep }: StepperProps) {
  return (
    <>
      <div className="grid grid-cols-4 cursor-pointer bg-gray-200 py-3 rounded-lg px-4">
        <button
          className="flex items-center   space-x-4"
          onClick={() => HandleStep(1)}
        >
          <div className="text-white font-poppins rounded-full flex  justify-center items-center sidebar-color w-9 h-9">
            <p className="text-lg font-semibold">1</p>
          </div>
          <p className="text-[#1D627B] text-lg font-poppins">
            Download template
          </p>
        </button>
        <button
          className="flex items-center   space-x-4"
          onClick={() => HandleStep(2)}
        >
          <div
            className={` font-poppins rounded-full flex  justify-center items-center ${
              step >= 2
                ? "sidebar-color text-white "
                : "bg-gray-300 text-gray-600"
            } w-9 h-9`}
          >
            <p className="text-lg font-semibold">2</p>
          </div>
          <p
            className={`${
              step >= 2 ? "text-[#1D627B]" : "text-gray-500"
            } text-lg font-poppins`}
          >
            Upload The File
          </p>
        </button>
        <button
          className="flex items-center   space-x-4"
          onClick={() => HandleStep(3)}
        >
          <div
            className={` font-poppins rounded-full flex  justify-center items-center ${
              step >= 3
                ? "sidebar-color text-white "
                : "bg-gray-300 text-gray-600"
            } w-9 h-9`}
          >
            <p className="text-lg font-semibold">3</p>
          </div>
          <p
            className={`${
              step >= 3 ? "text-[#1D627B]" : "text-gray-500"
            } text-lg font-poppins`}
          >
            Select A Supplier
          </p>
        </button>
        <button
          className="flex items-center   space-x-4"
          onClick={() => HandleStep(4)}
        >
          <div
            className={` font-poppins rounded-full flex  justify-center items-center ${
              step == 4
                ? "sidebar-color text-white "
                : "bg-gray-300 text-gray-600"
            } w-9 h-9`}
          >
            <p className="text-lg font-semibold">4</p>
          </div>
          <p
            className={`${
              step == 4 ? "text-[#1D627B]" : "text-gray-500"
            } text-lg font-poppins`}
          >
            Download Data
          </p>
        </button>
      </div>
      <hr
        className={`rounded-l-full bg-[#1D627B] h-1 smooth-transition  ${
          step == 2
            ? "w-2/4"
            : step == 3
            ? "w-3/4"
            : step == 4
            ? "w-full"
            : "w-1/4"
        }`}
      />
    </>
  );
}

export default Stepper;
