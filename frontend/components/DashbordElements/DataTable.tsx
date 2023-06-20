import { HeartIcon } from "@heroicons/react/20/solid";
import warning from "../../6897039.png"
import React, { useState } from "react";
import { ceil } from "lodash";
import { count } from "console";
import ToastErrorPanel from "../../utils/error-toast";

export default function DataTable({ head, body }: any) {
  // const [current, setCurrent] = useState(0);
  // const displayCount = 2;
  // const [totalCount, setTotalCount] = useState(body.length);
  // const [totalPage, setTotalPage] = useState(ceil(body.length / displayCount))

  // async function back() {
  //   if (current > 0) {
  //     setCurrent(current - 1);
  //   }
  // }

  // async function next() {
  //   if (current < totalPage - 1) {
  //     setCurrent(current + 1);
  //   }
  // }

  const bodyTable = () => {
    let arrayOfElements = []
    for (let i in body) {
      console.log(body[i], "-----------")
      arrayOfElements.push(<>
        <tr key={i} className="border-b hover:bg-odd-color bg-gray-50">
          <th scope="row" className="py-4 px-6 font-medium text-gray-900 text-center">
            {i + 1}
          </th>
          {
            rowTable(body[i])

          }
        </tr></>)
    }
    return arrayOfElements
  }


  const rowTable = (col) => {
    let loopArray = []
    for (let j in col) {
      console.log(col[j])
      loopArray.push(
        col[j] == "active" || col[j] == "ACTIVE" ?
          <td key={j} className="py-2 m-2 px-2 font-small text-gray-999 text-center">
            <img src={'https://cdn-icons-png.flaticon.com/512/4315/4315445.png'} className="px-9" />
            {col[j]}
          </td> : col[j] == "OBSOLETE" ?
            <>
              < td key={j} className="py-4 px-6 font-medium text-gray-900 text-center" >
                <img src={'https://cdn-icons-png.flaticon.com/32/6785/6785368.png'} className="px-4" />
                {col[j]}
              </td >
            </>
            : col[j] == "PREVIEW" ?
              < td key={j} className="py-55 px-60 font-medium text-gray-900 text-center" >
                <img src={'https://cdn-icons-png.flaticon.com/512/3840/3840662.png'} className="px-2" />
                {col[j]}
              </td > : col[j] == "NOT RECOMMENDED FOR NEW DESIGNS" ?
                < td key={j} className="py-4 px-6 font-medium text-gray-900 text-center" >
                  <img src={'https://cdn-icons-png.flaticon.com/256/6897/6897039.png'} className="px-4" />
                  {col[j]}
                </td > : col[j] == "LAST TIME BUY" ?
                  <>
                    < td key={j} className="py-4 px-6 font-medium text-gray-900 text-center" >
                      <img src={'https://cdn-icons-png.flaticon.com/256/6897/6897039.png'} className="px-4" />
                      {col[j]}
                    </td >
                  </>
                  : < td key={j} className="py-4 px-6 font-medium text-gray-900 text-center" >
                    {col[j]}
                  </td >
      )

    }
    return loopArray
  }

  return (
    <div className="px-4 min-w-full sm:px-6 lg:px-8 relative">
      {body.length >= 1 ? (
        <>
          <div className="text-center py-2 font-medium">{body.length && `Total Rows : ${body.length}`}</div>
          <div className="">
            <div className="overflow-x-auto relative shadow-md sm:rounded-lg" style={{ margin: "auto", maxWidth: `${window.innerWidth / 5 * 4}px` }}>
              <table className="w-full text-sm text-left text-gray-500">
                <thead className="tablebar-color text-white text-base h-20 bg-gray-50 ">
                  <tr>
                    <th scope="col" className="py-3 px-6 text-center">
                      Index
                    </th>
                    {
                      head.map((data: string, i: number) =>
                        <th key={i} scope="col" className=" text-center py-3 px-6">
                          {data.charAt(0).toUpperCase() + data.slice(1)}
                        </th>
                      )
                    }


                  </tr>
                </thead>
                <tbody>
                  {
                    bodyTable()
                  }

                </tbody>
              </table>
            </div>
            {/* <div className="flex justify-center gap-16 py-10">
            <div className="cursor-pointer" onClick={back}>back</div>
            <div className="cursor-pointer" onClick={next}>next</div>
          </div> */}
          </div>
        </>

      ) : (
        <ToastErrorPanel message="Data not found or temporarily unavailable" />
        // <p className="text-center text-xl py-4">
        //   Data not found or temporarily unavailable :(
        // </p>
      )}
    </div>
  );
}
