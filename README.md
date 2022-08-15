
[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Source+Code+Pro&duration=7000&pause=1000&color=478BC2&vCenter=true&width=435&lines=%5B01101000+01101001%5D)](https://git.io/typing-svg)

# Exstego

A small steganography app that provides certain attack and embed methods.



## Features

Demonstrates the flow of some attacks and the process of extracting and destroying data.

Logs and results are saved in the folder relative to the app: *./RESULTS/...*


**LSB steganography**

Params:


    Color channels: ['red', 'green', ['blue']
    Embed methods: ['Scatter', 'Sequential']
    Percentage: [0,..., 1]

    

| Method | Description |
| ------ | ------ |
| Sequential | Embed/ extract/ destroy starting from the first pixel |
| Scatter | Start from beggining and skip pixels in order to cover the whole file|

Percentage determens how much of the image will be altered, as well as the step of the scatter method.

<br>

**METADATA steganography**

Params:

    Metadata key: {metadata_type}.{metadata_namespace}.{metadata_key}

All available tags can be found on the link: [exiv2 tags list](https://exiv2.org/index.html)

Library Github profile: [exiv2 github](https://github.com/Exiv2/exiv2)

<br>

**BPCS steganography**

Params:

    Color channels: ['red', 'green', 'blue']
    Bit planes: [0,..., 8]

<br>
<br>

**Attacks**

Analytical (need both *stego* and *original* file, used for detecting):

- Compare bit planes of stego and original file
- Compare histograms of stego and original file

<br>

Stego oriented (used extraction, detection or destruction):

- Split bit planes
- Overlap bit planes
- Destroy data in LSBs
- Destroy metadata information
- Extract metadata

<br>
<br>

**Embed methods**
- LSB steganography
- METADATA steganography


## Appendix

Useful demo links:
  - [Exiv2 Github](https://github.com/Exiv2/exiv2)
  - [Exiv2 available tags list](https://exiv2.org/index.html)

<br>

BPCS planes overlap function was inspired by a solved problem:
- [Stackoverflow - Python image manipulation](https://stackoverflow.com/questions/58194992/python-image-manipulation-using-pillsb)

## Demo

**Notes**

Console logging can be disabled in code (./app/exstego.py):

<img src="./demo/logger-disable-print.png" height=210 width=auto>

<br>


## Tech

**Environment:** PyCharm

**Languages:** KivyMD, Python v3.10

| PyCharm | KivyMD | Python v3.10 |
| ------ | ------ | ------ |
| <img src="./readme_resources/tech-logos/logo-pycharm.png" width=auto height=70> | <img src="./readme_resources/tech-logos/logo-kivymd.png" width=auto height=70> |  <img src="./readme_resources/tech-logos/logo-python.png" width=auto height=70> |


## Authors

- [@v-gabriel](https://github.com/v-gabriel)

