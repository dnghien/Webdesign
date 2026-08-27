let bedrooms = 3;
const taxRate = 0.08;

if (bedrooms > 3) {
    console.log("You have a large house.");
    console.warn("Warning: Large houses may have higher maintenance costs.");
    console.error("Error: Please ensure you have the necessary resources for a large house.");
} else {
    console.log("You have a small house.");
}

for (let i = 0; i <= bedrooms; i++) {
    console.log('Bedroom ${i}');
}

let sample = { id: 1, name: "Sample Object", type: "Example" };

console.log("Sample Object:", sample);
console.log("Sample Object ID:", sample.id);


let arr = [{ name: "Maths", score: 8 }, { name: "Programming", score: 9 }, { name: "English", score: 7 }];
let sum = 0;
let max = 0;

for (let i = 0; i < arr.length; i++) {
    sum += arr[i].score;
    if (arr[i].score > 8) {
        console.log("Subject with score > 8: " + arr[i].name);
    }
    if (arr[i].score > max) {
        max = arr[i].score;
    }
}

console.log("Sum of scores: " + sum);
console.log("Maximum score: " + max);
