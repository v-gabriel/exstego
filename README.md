
[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Source+Code+Pro&duration=7000&pause=1000&color=478BC2&vCenter=true&width=435&lines=%5B01101000+01101001%5D)](https://git.io/typing-svg)

# Exstego

A small steganography app that provides certain attack and embed methods.



## Features

Demonstrates the flow of some attacks and the process of extracting and destroying data.

**Steganography methods**

LSB steganography
 -


Params:


    Color channels: ['red', 'green', ['blue']
    Embed methods: ['Scatter', 'Sequential']
    Percentage: [0,..., 1]

    

| Method | Description |
| ------ | ------ |
| Sequential | Embed/ extract/ destroy starting from the first pixel |
| Scatter | Start from beggining and skip pixels in order to cover the whole file|

Percentage determens how much of the image will be altered, as well as the step of the scatter method.


METADATA steganography
 - 

Params:

    Metadata key: {metadata_type}.{metadata_namespace}.{metadata_key}

All available tags can be found on the link: [exiv2 tags list](https://exiv2.org/index.html)

Library Github profile: [exiv2 github](https://github.com/Exiv2/exiv2)


BPCS steganography
 -

Params:

    Color channels: ['red', 'green', 'blue']
    Bit planes: [0,..., 8]

---
<br>

**Attacks**

Analytical
 -
    
Need both *stego* and *original* file, used for detecting:

- Compare bit planes of stego and original file
- Compare histograms of stego and original file

Stego oriented
 - 

Used extraction, detection or destruction:

- Split bit planes
- Overlap bit planes
- Destroy data in LSBs
- Destroy metadata information
- Extract metadata

<br>

**Embed methods**
- LSB steganography
- METADATA steganography


## Appendix

Useful demo links:
  - [Exiv2 Github](https://github.com/Exiv2/exiv2)
  - [Exiv2 available tags list](https://exiv2.org/index.html)

---
<br>

BPCS planes overlap function was inspired by a solved problem:
- [Stackoverflow - Python image manipulation](https://stackoverflow.com/questions/58194992/python-image-manipulation-using-pillsb)
Extended to choose custom planes to overlap.

## Demo

TODO


## Tech Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 

![PyCharm](https://img.shields.io/badge/pycharm-143?style=for-the-badge&logo=pycharm&logoColor=black&color=black&labelColor=green)

**Environment:** PyCharm

**Languages:** KivyMD, Python v3.10

<img src="app/images/tech-logos/logo-python" width="100" height="100">

<img src="app/images/tech-logos/logo-kivymd" width="100" height="100">

<img src="app/images/tech-logos/logo-pycharm" width="100" height="100">




## Authors

- [@v-gabriel](https://github.com/v-gabriel)

