import axios from "axios";

export default async function fetchMouser(partnumber: string) {
  try {
    const resp = await axios.post(
      "https://api.mouser.com/api/v1/search/partnumber?apiKey=c8cc8913-3363-4547-a4f6-d48218731924",
      {
        SearchByPartRequest: {
          mouserPartNumber: partnumber,
        },
      }
    );

    if (resp?.data?.SearchResults?.Parts.length !== 0) {
      console.log(resp?.data?.SearchResults.Parts);
      return resp?.data?.SearchResults?.Parts;
    } else {
      console.log("Err");
      return [{ status: "not found" }];
    }
  } catch (err) {
    console.log(err);
    return [{ status: "not found" }];
  }
}

export async function fetchFutureElectronics(partnumber: string) {
  try {
    const resp = await axios.get(
      `https://api.futureelectronics.com/api/v1/pim-future/lookup/?part_number=${partnumber}`,
      {
        headers: {
          "x-orbweaver-licensekey": "GAQZI-7GNVU-QNH36-Y4QUX-607ON",
          Accept: "application/json,text/javascript",
          "Content-Type": "application/json",
        },
      }
    );
    console.log(resp.data.offers[0]);
    if (resp?.data?.offers.length != 0) {
      return [
        {
          status: "found",
          mpn: resp.data.offers[0].quantities.quantity_available || "NOT FOUND",
          "available quantity":
            resp.data.offers[0].quantities.quantity_on_order || "NOT FOUND",
          "quantity on order":
            resp.data.offers[0].quantities.quantity_on_order || "NOT FOUND",
          category: resp.data.offers[0].categories[0].name || "NOT FOUND",
          "seller partnumber":
            resp?.data?.offers[0].part_id.seller_part_number || "NOT FOUND",
        },
      ];
    } else {
      return [{ status: "not found" }];
    }
  } catch (err) {
    console.log(err);
    return [{ status: "not found" }];
  }
}
export async function fetchDigiKey(partnumber: string) {
  try {
    const resp = await axios.get(
      `http://localhost:3000/api/fetch_digikey?partNumber=${partnumber}`
    );

    if (resp?.data.length != 0) {
      return resp.data;
    } else {
      return [{ status: "not found" }];
    }
  } catch (err) {
    console.log(err);
    return [{ status: "not found" }];
  }
}

export async function findSupplier(partnumber: string) {
  let suppliers = [];
  try {
    const response = await fetchMouser(partnumber);
    if (response && response[0].status !== "not found") {
      suppliers.push("mouser");
    }
  } catch (err) {
    console.log(err);
  }

  try {
    const response = await fetchFutureElectronics(partnumber);
    if (response[0]?.status !== "not found") {
      suppliers.push("futureelectronics");
    }
  } catch (err) {
    console.log(err);
  }

  return suppliers;
}
