# tasklib Architecture

## Overview

tasklib is organized as a **five-layer dependency chain**. Each layer depends only on the layers below it -- never on layers above it and never on peer layers at the same level. This strict ordering ensures that PRs can be merged sequentially, with each layer validated before anything that depends on it is introduced.

The five layers, from bottom (Layer 0) to top (Layer 4):

| Layer | Name             | Purpose                                           |
|