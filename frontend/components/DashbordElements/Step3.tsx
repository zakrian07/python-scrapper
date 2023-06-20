/* eslint-disable react-hooks/rules-of-hooks */
import React, { useState } from "react";
import suppliersList from "../../utils/suppliers";
import { useAppSelector, useAppDispatch } from "../../Redux/hooks";
import {
  setSupplier,
  setSupplierType,
  selectSupplierType,
} from "../../Redux/Slices/StepperSlice";

interface stepProps {
  nextStep: () => void;
}
function step3({ nextStep }: stepProps) {
  const dispatch = useAppDispatch();
  const supplierType: string = useAppSelector(selectSupplierType);
  const AddSupplierToRedux = (supplier: string) => {
    dispatch(setSupplier(supplier));
  };

  const AddSupplierTypeToRedux = (type: string) => {
    dispatch(setSupplierType(type));
  };

  function AddSupplierInfo(type: string, supplier: string) {
    AddSupplierTypeToRedux(type);
    AddSupplierToRedux(supplier);
  }

  return (
    <>
      <div className="bg-gray-200 rounded-lg space-y-3 px-5 py-24 mt-9 ">
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-lg bg-gray-300 px-5 py-9 ">
            <h1 className="text-2xl font-poppins text-center text-[#225373]">
              Manufacturer
            </h1>
            <select
              name="Type of supplier"
              className={`w-full  mt-12 smooth-transition ${supplierType == "distributer" ? "opacity-60" : ""
                } min-h-[50px] rounded-lg font-poppins text-lg cursor-pointer hover:shadow-lg shadow-md border-0`}
              onChange={(e) => AddSupplierInfo("manufacturer", e.target.value)}
            >
              <option value="">Select supplier</option>
              {suppliersList.manufacturers.map((manufacturer, i) => (
                <option key={i} value={manufacturer}>
                  {manufacturer}
                </option>
              ))}
            </select>
          </div>
          <div className="rounded-lg bg-gray-300  px-5 py-9  ">
            <h1 className="text-2xl text-center font-poppins text-[#225373] ">
              Distributer
            </h1>
            <select
              name="Type of supplier"
              className={`w-full mt-12  smooth-transition min-h-[50px] ${supplierType == "manufacturer" ? "opacity-60" : ""
                } rounded-lg font-poppins text-lg cursor-pointer hover:shadow-lg shadow-md border-0`}
              onChange={(e) => AddSupplierInfo("distributer", e.target.value)}
            >
              <option value="">Select supplier</option>
              {suppliersList.distributers.map((distributer, i) => {
                if (distributer === ("R-S Hughes")) {
                  return (<option key={i} value={distributer} className="text-red">
                    {distributer}
                  </option>)
                }
                else {
                  return (<option key={i} value={distributer}>
                    {distributer}
                  </option>)
                }
              }
              )}
            </select>
          </div>
        </div>
      </div>
      {supplierType && (
        <div className="flex justify-center items-center mt-7">
          <button
            className="border border-gray-400 sidebar-color rounded-lg text-white font-poppins text-lg px-16 py-2 "
            onClick={nextStep}
          >
            Continue
          </button>
        </div>
      )}
    </>
  );
}

export default step3;
