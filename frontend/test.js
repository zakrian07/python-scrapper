axios = require("axios");
const call = async () => {
  const resp = await axios.get(
    `https://api.futureelectronics.com/api/v1/pim-future/lookup/?part_number=AL5890-30P1-13`,
    {
      headers: {
        "x-orbweaver-licensekey": "GAQZI-7GNVU-QNH36-Y4QUX-607ON",
        Accept: "application/json,text/javascript",
        "Content-Type": "application/json",
      },
    }
  );
  console.log(resp.data.offers[0].categories[0].name);

  if (resp?.data?.offers.length != 0) {
    console.log([
      {
        mpn: resp.data.offers[0].quantities.quantity_available,
        "available quantity": resp.data.offers[0].quantities.quantity_on_order,
        "quantity on order": resp.data.offers[0].quantities.quantity_on_order,
        category: resp.data.offers[0].categories[0].name,
        "seller partnumber": resp?.data?.offers[0].part_id.seller_part_number,
      },
    ]);
  }
};

call();
