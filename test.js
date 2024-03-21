// const numeric = require('numeric');

import data from './optimal_power.json' assert {type: 'json'};
// const spline = numeric.spline(data.distance, data.power)

window.onload = function() {
    document.getElementById('displayButton').addEventListener('click', function() {
        document.getElementById('optimizationResultsContainer').innerText = JSON.stringify(data.power, null, 2);
    });
    document.getElementById('hideButton').addEventListener('click', function() {
        document.getElementById('optimizationResultsContainer').innerText = '';
    });
    document.getElementById('inputfield').addEventListener('input', function(event) {
        const distance = parseFloat(event.target.value);
        if (!isNaN(distance)) {
            let optimalPower = spline.at(distance);
            document.getElementById('optimalPowerContainer').innerText = optimalPower;
        }
    });

    // document.getElementById('runOptimizationButton').addEventListener('click', async () => {
    //     const path = "test.py";
    //     try {
    //         const response = await fetch('http://127.0.0.1:5000/run-script', {
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json'
    //             },
    //             body: JSON.stringify({ path: path })
    //         });
    //         if (!response.ok) {  // Check if the request was successful
    //             throw new Error(`HTTP error! status: ${response.status}`);
    //         }
    //         data = await response.json();  // Assign the response to the global 'data' variable
    //         console.log("Python script ran successfully")
    //         console.log(data.result);
            

    //     } catch (error) {
    //         console.log(error);  // Log any errors
    //     }
    // });
};



// async function runOptimizationScript() {
//     const path = "main.py";
//     const response = await fetch('/run-script', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ path: path })
//     });
//     const data = await response.json();
//     console.log(data.result);
// }