# Labelled Egocentric Temporal Network Generation

---

In this repository we include the data and the code for the generation of labelled temporal networks with the LETN method, presented in [this pre-print](https://doi.org/10.48550/arXiv.2501.07327).

Our method takes as input a temporal network, and looks at local patterns, grouping patterns of nodes with the same attribute, thus resulting in a generation that takes into account communities when the attribute is the community the nodes belong to.

This is particularly relevant when producing surrogate networks to study face-to-face interactions. For this reason we tested our method with the [SocioPatterns](http://www.sociopatterns.org/) datasets.


## Usage

In this repo we include the notebook `Usage.ipynb`, in which we show how to use our module. You can plug-in your dataset by simply changing the file names. In our files we include the edges in the following format: `timestamp  node1  node2`. The files with the metadata (if available) have the following format: `node  metadata`.



## Citation

If you find the paper and this code useful, please cite us (journal publication under review) as:

```bibtex
@article{girardini2025community,
  title={Community Aware Temporal Network Generation},
  author={Girardini, Nicol{\`o} Alessandro and Longa, Antonio and Trebucchi, Gaia and Cencetti, Giulia and Passerini, Andrea and Lepri, Bruno},
  journal={arXiv preprint arXiv:2501.07327},
  year={2025},
  doi={https://doi.org/10.48550/arXiv.2501.07327}
}
```