interface Supliers {
  manufacturers: string[];
  distributers: string[];
}

const manufacturers: string[] = [


  "Abracon, LLC",
  "Allegro",
  "Alpha Wire Corp",
  "Analog Devices",
  "Belfuse",
  "Bivar",
  //"Eaton",
  "Fair Rite",
  "Festo",
  "Hamlin Electronics",
  "Infineon",
  //"Littelfusse",
  "Leespring",
  "Maxim Integrated",
  //"Mmm",
  "Microchip",
  "Molex",
  "Murata Manufacturing Co",
  //"Murata",
  "Newark Electronics Corporation",
  "Omron",
  "Onsemi",
  "Panduit",
  "Panasonic",
  "Phoenix",
  "Radiall",
  "Semtech",
  "STMicroelectronics",
  "Skywork Solution",
  "Taiyo Yuden",
  "TDK",
  "TE",
  "Texas Instruments",
  "Vishay Intertechnology",
  "Wago",
  //"We-online",
  "Yageo",
  //"Yago",

];

const distributers: string[] = [
  "Arrow",
  "Allied Electronics",
  // "Anixter",
  "Digikey",
  // "Ttiinc",
  // "Maxim",
  "Future Electronics",
  // "Heilind Electronics",
  // "Alliedelec",
  // "Newark",
  // "Farnell",
  "Mouser Electronics",
  "McMaster-Carr Supply Company",
  // "Sager",
  // "Rshughes",
  "Rs-components",
  "R-S Hughes (currently unavailable)",
  "Sager",
  "TTI",
];

const suppliersList: Supliers = {
  manufacturers,
  distributers,
};
export default suppliersList;
