import React, { useState } from "react";
import DahbordHeader from "./DahboardHeader";
import Step1 from "./Step1";
import Step2 from "./Step2";
import Step3 from "./Step3";
import Step4 from "./Step4";

import Stepper from "./Stepper";
import suppliersList from "../../utils/suppliers";
function Generate() {
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const [step, setstep] = useState(1);
  function NextStep() {
    setstep(step + 1);
  }
  function HandleStep(value: number) {
    if (value > step) return;
    setstep(value);
  }
  return (
    <div className="">
      <DahbordHeader title="Upload Data" />
      <div className="mt-9">
        <Stepper step={step} HandleStep={HandleStep} />
        {step == 1 ? (
          <Step1 nextStep={NextStep} />
        ) : step == 2 ? (
          <Step2 nextStep={NextStep} />
        ) : step == 3 ? (
          <Step3 nextStep={NextStep} />
        ) : (
          <Step4 />
        )}
      </div>
    </div>
  );
}

export default Generate;
