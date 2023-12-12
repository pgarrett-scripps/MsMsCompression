function floatToHex(f) {
    const buffer = new ArrayBuffer(4);
    new Float32Array(buffer)[0] = f;
    return [...new Uint8Array(buffer)].reverse().map(b => b.toString(16).padStart(2, '0')).join('');
}

function hexToFloat(hex) {
    const uint = new Uint32Array(new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16))).buffer)[0];
    return new Float32Array([uint])[0];
}

function encodeLeadingZero(lz) {
    if (lz >= 0 && lz < 16) {
        return lz.toString(16);
    } else {
        throw new Error("Value must be between 0 and 15 (inclusive)");
    }
}

function reverseHexString(hexString) {
    return hexString.match(/.{2}/g).reverse().join('');
}

function hexDelta(a, b) {
    const diff = parseInt(a, 16) - parseInt(b, 16);
    return (diff >>> 0).toString(16).padStart(8, '0');
}

function countLeadingZeros(str) {
    return str.match(/^0*/)[0].length;
}

function encodeMzs(mzs) {
    const mzsHex = mzs.map(floatToHex);
    const initialHexValue = mzsHex[0];
    const initialHexValueZeros = countLeadingZeros(initialHexValue);
    const mzsHexDeltas = mzsHex.slice(1).map((hex, i) => hexDelta(hex, mzsHex[i]));
    const leadingZeros = mzsHexDeltas.map(countLeadingZeros);
    const hexDeltaStr = initialHexValue.slice(initialHexValueZeros) +
                        mzsHexDeltas.map((hex, i) => hex.slice(leadingZeros[i])).join('');
    const leadingZeroStr = encodeLeadingZero(initialHexValueZeros) +
                           leadingZeros.map(encodeLeadingZero).join('');
    return hexDeltaStr + leadingZeroStr.split('').reverse().join('');
}


function encodeIntensities(intensities) {
    return intensities.map(floatToHex).join('');
}

function splitPeaks(peaksArray) {
    const mzArray = peaksArray.map(peak => parseFloat(peak[0]));
    const intensityArray = peaksArray.map(peak => parseFloat(peak[1]));
    return [mzArray, intensityArray];
}

function CompressUrlLzstring(mzs, intensities) {
    let mz_str = encodeMzs(mzs);
    let int_str = encodeIntensities(intensities);
    const combinedData = JSON.stringify([mz_str, int_str]);
    return LZString.compressToEncodedURIComponent(combinedData);
}


