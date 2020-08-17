<p align="center">
  <img 
    src="https://i.imgur.com/H5lyBFn.png" 
    width="120px"
    alt="ICONation logo">
</p>

<h1 align="center">MultiSigWallet</h1>

 [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Introduction

MultiSigWallet is a fully **open source**, **free** service that allows any ICONist to **safely trade** with anyone IRC2 tokens against any other.

It is an alternative solution to the [Over-The-Counter](https://www.investopedia.com/terms/o/otc.asp) (OTC) trading method taking place on few unlisted tokens on ICON.

Alternatively, MultiSigWallet may be used by other SCORE developers willing to implement a token swap in their contract : the MultiSigWallet SCORE contract may be called from another SCORE.

You can read and **review the open source code** here :

SCORE GitHub : [https://github.com/iconation/MultiSigWallet-SCORE](https://github.com/iconation/MultiSigWallet-SCORE)

GUI GitHub : [https://github.com/iconation/MultiSigWallet](https://github.com/iconation/MultiSigWallet) 


## Table of Contents

## Developers Quick Start

Here is a checklist you will need to follow in order to deploy MultiSigWallet to the Yeouido testnet:

  * Install prerequisites:
    * `python3 -m venv ./venv && source ./venv/bin/activate`
    * `pip install tbears`
    * `sudo apt install jq`
  * Clone the MultiSigWallet repository:
    * `git clone https://github.com/iconation/MultiSigWallet.git && cd MultiSigWallet`
  * Start tbears using the `start_tbears.sh` script located at the root folder of the MultiSigWallet repository
    * `./start_tbears.sh`
  * Install the operator wallets:
    * `./install.sh`
    * It will generate 3 operator wallets : 
      * A first one on the Yeouido network in `./config/yeouido/keystores/operator.icx`
      * A second one on the Euljiro network in `./config/euljiro/keystores/operator.icx`
      * A last one on the Mainnet network in `./config/mainnet/keystores/operator.icx`
    * Input a password for each network
  * Send few ICX (20 ICX should be enough) to the Yeouido wallet (the newly generated address is displayed after executing the `install.sh` script)
    * If you don't have some testnet ICX, use the [faucet](http://icon-faucet.ibriz.ai/) or contact [@Spl3en](https://t.me/Spl3en)
  * Deploy your SCORE to the testnet:
    * `./scripts/score/deploy_score.sh -n yeouido`
    
## Deploy MultiSigWallet SCORE to localhost, testnet or mainnet

- In the root folder of the project, run the following command:
<pre>./scripts/score/deploy_score.sh</pre>

- It should display the following usage:
```
> Usage:
 `-> ./scripts/score/deploy_score.sh [options]

> Options:
 -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)
```

- Fill the `-n` option corresponding to the network you want to deploy to: `localhost`, `yeouido`, `euljiro` or `mainnet`.
- **Example** : 
<pre>$ ./scripts/score/deploy_score.sh -n localhost</pre>

## Update an already deployed MultiSigWallet to localhost, testnet or mainnet

- If you modified the MultiSigWallet SCORE source code, you may need to update it.

- In the root folder of the project, run the following command:
<pre>$ ./scripts/score/update_score.sh</pre>

- It should display the following usage:
```
> Usage:
 `-> ./scripts/score/update_score.sh [options]

> Options:
 -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)
```

- Fill the `-n` option corresponding to the network where your SCORE is deployed to: `localhost`, `yeouido`, `euljiro` or `mainnet`.

- **Example** :
<pre>$ ./scripts/score/update_score.sh -n localhost</pre>
