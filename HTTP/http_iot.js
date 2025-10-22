// Câu a
// GET API
async function getItems() {
  try {
    const res = await fetch(
      "https://api.thingspeak.com/update?api_key=PDK7V4MC6UFSLZIT&field1=20&field2=50&field3=20225426"
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    return items;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
// Response
const res = await getItems();
console.log("Câu a");
console.log(res);

// Câu b
async function getResult() {
  try {
    const res = await fetch(
      "https://api.thingspeak.com/channels/3100276/feeds.json?results=10"
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
const resData = await getResult();
const result = resData.feeds;

function Avg(arr) {
  let avg = 0;
  arr.forEach((e) => {
    avg += e;
  });
  return avg / arr.length;
}

function standardDeviation(arr) {
  const n = arr.length;
  if (n === 0) return 0;
  const mean = arr.reduce((acc, val) => acc + val, 0) / n;
  const variance = arr.reduce((acc, val) => acc + (val - mean) ** 2, 0) / n;
  return Math.sqrt(variance);
}

const field1 = result.map((e) => +e.field1);
const field2 = result.map((e) => +e.field2);

console.log("\nCâu b");
console.log(`Giá trị trung bình của Field1: ${Avg(field1)}`);
console.log(`Giá trị trung bình của Field2: ${Avg(field2)}`);
console.log(`Độ lệch chuẩn của Field1: ${standardDeviation(field1)}`);
console.log(`Độ lệch chuẩn của Field2: ${standardDeviation(field2)}`);

// Câu c
async function getToken() {
  try {
    const res = await fetch("https://iot-api.deno.dev/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "tung.nx225426@sis.hust.edu.vn",
        mssv: "20225426",
      }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    return items.token;
  } catch (err) {
    console.error(err);
    throw err;
  }
}

const token = await getToken();
console.log("\nCâu c");
console.log(`Token: ${token}`);

// Câu d
async function getTimestamp() {
  try {
    const res = await fetch("https://iot-api.deno.dev/api/get_data", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    return items;
  } catch (err) {
    console.error(err);
    throw err;
  }
}

function formatDateTimeUTC(str) {
  const date = new Date(str);

  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const day = String(date.getUTCDate()).padStart(2, "0");
  const hours = String(date.getUTCHours()).padStart(2, "0");
  const minutes = String(date.getUTCMinutes()).padStart(2, "0");
  const seconds = String(date.getUTCSeconds()).padStart(2, "0");

  return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
}

const data = await getTimestamp();
console.log("\nCâu d");
console.log(`Nhiệt độ: ${data.temp}`);
console.log(`Độ ẩm: ${data.humid}`);
console.log(`Thời gian: ${formatDateTimeUTC(data.timestamp)}`);
