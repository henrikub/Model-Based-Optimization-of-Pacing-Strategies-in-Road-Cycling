const numeric = require('numeric');
const distance = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
const power = [300, 290, 290, 299, 280, 275, 275, 275, 260, 240, 234]
const spline = numeric.spline(distance, power)
const interpolated_spline = spline.at(5)
console.log(interpolated_spline)
function linear_interpolation(x, x_arr, y_arr) {
    let i = 0;
    let x1, x2, y1, y2;
    while (x > x_arr[i+1]) {
        
        x1 = x_arr[i];
        y1 = y_arr[i];
        x2 = x_arr[i+1];
        y2 = y_arr[i+1];
        i++;
    }
    console.log(x2, x1)
    return y1 + ((x-x1) * (y2-y1)) / (x2-x1)
}
console.log(linear_interpolation(13, distance, power))
function get_target_power(distance, distance_arr, power_arr) {
    let index = 0;
    let min_diff = Math.abs(distance - distance_arr[0]);
    for (let i = 1; i < distance_arr.length; i++) {
        let difference = Math.abs(distance - distance_arr[i]);
        if (difference < min_diff) {
            min_diff = difference;
            index = i;
        }
    }
    return power_arr[index];
}
console.log(get_target_power(96, distance, power))