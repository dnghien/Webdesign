async function greet() {
    return "Hello, World!";
}

console.log(greet());

//c1
async function getData() {
    let text = ""
    greet().then((response) => {
        text = response;
    });
    return text;
}
console.log(getData());

async function getData() {
    const text = await greet();
    console.log(text);
}

getData();