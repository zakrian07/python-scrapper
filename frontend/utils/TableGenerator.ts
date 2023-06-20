import { isArray } from "lodash";

const config = {
  headers: {
    "Content-type": "application/json",
  },
};
let head: any[] = [];
let body: any[] = [];
let tabledata = { head, body };

export function generateTableData(data: any) {
  for (let d of data) {
    head = Object.keys(d);
  }

  tabledata.head = head;
  tabledata.body = [];
  for (let d of data) {
    // console.log(d)
    const d_arr = [];
    for (let h of head) {
      console.log(h)
      if (isArray(d[h]) && d[h].length == 0) {
        d_arr.push("Not Available");
      }
      else if (d[h]) {
        d_arr.push(d[h]);
      }
      else {
        d_arr.push("Not Available");
      }
    }
    tabledata.body.push(d_arr);
  }
  return tabledata;
}

export function generateDigiKeyTable(data: { [x: string]: any }) {
  tabledata.head = [
    "DigiKeyPartNumber",
    "Manufacturer",
    "ManufacturerPartNumber",
    "ProductDescription",
    "DetailedDescription",
    "PrimaryDatasheet",
    "Category",
    "Series",
    "ProductStatus",
    "RoHSStatus",
    "MoistureSensitivityLevel",
    "ECCN",
    "HTSUSCode",
  ];
  tabledata.body = [];
  let temp = [];
  for (let h of tabledata.head) {
    if (h == "Manufacturer") {
      temp.push(data["Supplier"]);
    } else if (h == "ECCN") {
      temp.push(data["ExportControlClassNumber"]);
    } else if (h == "ProductStatus") {
      temp.push(data["ProductStatus"]);
    } else if (h == "Series") {
      temp.push(data["Series"].Value);
    } else if (h == "Category") {
      temp.push(data["Category"].Value);
    } else {
      temp.push(data[h]);
      console.log(temp);
    }
  }

  tabledata.body.push(temp);
  return tabledata;
}

export function generateMouserTableData(data: any) {
  for (let d of data) {
    if (Object.keys(d).length > head.length) tabledata.head = Object.keys(d);
  }
  tabledata.body = [];
  for (let d of data) {
    const d_arr = [];
    for (let h of tabledata.head) {
      if (h == "ProductCompliance") {
        let compliances = [];
        for (let compliance of d[h]) {
          compliances.push(compliance.ComplianceName);
        }
        d[h] = compliances.join("-");
      } else if (h == "PriceBreaks") {
        let prices = [];
        if (d[h].length > 1) {
          for (let Pricebreak of d[h]) {
            prices.push(Number(Pricebreak.Price.replace("$", "")));
          }
          d[h] = `from ${Math.min(...prices)}$ to ${Math.max(...prices)}$`;
        } else if (d[h].length == 1) {
          d[h] = d[h][0].Price;
        } else {
          d[h] = "not found";
        }
      } else if (h == "ProductAttributes") {
        const attributes = [];
        if (d[h].length > 1) {
          for (let attribute of d[h]) {
            attributes.push(attribute.AttributeName);
          }
          d[h] = attributes.join("~");
        } else if (d[h].length == 1) {
          d[h] = d[h][0].AttributeName;
        } else {
          d[h] = "not found";
        }
      } else if (h == "UnitWeightKg") {
        d[h] = d[h]?.UnitWeight || "not found";
      }

      if (isArray(d[h]) && d[h].length == 0) {
        d_arr.push("Not Available");
      }
      else if (d[h]) {
        d_arr.push(d[h]);
      }
      else {
        d_arr.push("Not Available");
      }
    }
    tabledata.body.push(d_arr);
  }
  return tabledata;
}
