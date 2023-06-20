import React, { useState } from "react";

export default function DataTable({
  head,
  body,
  step = 10,
  Export = null,
}: any) {
  const [Start, setStart] = useState(0);
  const [End, setEnd] = useState(step);
  const NextPage = () => {
    if (End + step < body?.length) {
      setStart(Start + step);
      setEnd(End + step);
    } else if (body?.length < step) {
    } else {
      console.log(body.length);
      setStart(body?.length - step);
      setEnd(body?.length);
    }
  };

  const PreviousPage = () => {
    console.log(Start, End);
    if (!(Start - step < 0)) {
      setStart(Start - step);
      setEnd(End - step);
    } else {
      setStart(0);
      setEnd(step);
    }
  };

  return (
    <div className="mg-16 mt-5 table-shadow bdr-8 px-4">
      {body?.length != 0 && (
        <div className="w-full relative py-2 font-bold flex items-center justify-center">
          {Export !== null && (
            <div
              className="absolute left-0 bg-[#2F80ED] text-white font-mono px-6 py-1 rounded-md cursor-pointer "
              onClick={Export}
            >
              Export
            </div>
          )}
          <p>Total Rows : {body?.length} </p>
        </div>
      )}
      <div
        className="btl-8 btr-8"
        style={{
          width: "100%",
          maxHeight: "70vh",
          overflow: "auto",
          fontSize: "small",
        }}
      >
        <table className="relative w-full rounded-lg overflow-hidden">
          <thead className="">
            <tr className="text-[16px] font-bold bg-gradient-to-t from-[#0ec4c1] to-[#3f7599]  text-gray-100 ">
              {head?.map((column: any) => (
                <th key={"tbh_vw" + column} className="p-5 ">
                  {" "}
                  {column?.toString()}{" "}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {body?.slice(Start, End)?.map((row: any, index: any) => (
              <tr
                key={index + "tr"}
                className={`rounded-xl text-lg ${
                  index % 2 !== 0 ? "bg-[#bce7e7]" : "bg-gray-200"
                }`}
              >
                {row?.map((cell: any, cell_index: any) => (
                  <td
                    key={cell_index + "td" + index}
                    className="text-center py-4"
                  >
                    {cell?.toString()}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {body.length > 10 && (
        <div className="flex space-x-16 justify-center mt-5">
          <button
            className={`  py-3 px-5 font-semibold rounded-xl cursor-pointer ${
              Start === 0 || body?.length === 1
                ? "bg-gray-200 disabled"
                : "bg-gradient-to-t from-[#0ec4c1] to-[#3f7599]"
            } `}
            onClick={PreviousPage}
          >
            {"<< back"}
          </button>
          <button
            className={`  py-3 px-5 font-semibold rounded-xl cursor-pointer ${
              End === body?.length || body?.length < step
                ? "bg-gray-200 disabled"
                : "bg-gradient-to-t from-[#0ec4c1] to-[#3f7599]"
            }`}
            onClick={NextPage}
          >
            {"next >>"}
          </button>
        </div>
      )}
    </div>
  );
}
