<p align="center">
  <img 
    src="https://i.imgur.com/Ei7w5Om.png" 
    width="520px"
    alt="ICONSafe logo">
</p>

 [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Introduction

ICONSafe is a multisig wallet with advanced user managment. It is mostly useful for teams willing to share mutual funds. It is able to track tokens balance over time, and send/eceive any type of transactions. All outgoing transactions require confirmations from the wallet owners based on a vote before being executed. An outgoing transaction may contain multiple sub-transactions which are executed at the same time, so it is possible to create complex operations suiting for all type of situations.

## Table of Contents

## Developers Quick Start

Here is a checklist you will need to follow in order to deploy ICONSafe to the Yeouido testnet:

  * Install prerequisites:
    * `python3 -m venv ./venv && source ./venv/bin/activate`
    * `pip install tbears`
    * `sudo apt install jq`
  * Clone the ICONSafe repository:
    * `git clone https://github.com/iconation/ICONSafe.git && cd ICONSafe`
  * Bootstrap tbears using the `bootstrap_tbears.sh` script located in the tbears folder of the ICONSafe repository
    * `./tbears/bootstrap_tbears.sh`
  * Everytime you want to keep working on this contract, start tbears using the `start_tbears.sh` script located in the tbears folder of the ICONSafe repository
    * `./tbears/start_tbears.sh`
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
    
## Deploy ICONSafe SCORE to localhost, testnet or mainnet

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

## Update an already deployed ICONSafe to localhost, testnet or mainnet

- If you modified the ICONSafe SCORE source code, you may need to update it.

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
