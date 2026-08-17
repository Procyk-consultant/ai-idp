---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/CRYPTO_BACKEND_COMPLETION_2026-08-17.md
Title: Cryptographic Backend Source Completion — 2026-08-17
Version: 2.0.0-reconciliation
Status: SOURCE IMPLEMENTED / LIVE EXTERNAL VALIDATION PENDING
Branch: reconcile-2026-08-14
Last Material Revision: 2026-08-17
---

# Cryptographic Backend Source Completion — 2026-08-17

## 1. Decision

The cryptographic capabilities previously represented only by interfaces, migration architecture, or `NotImplementedError` branches were not removed or downgraded. The reconciliation branch now contains concrete source implementations for the targeted high-assurance signing paths.

This record distinguishes **source implementation** from **live target-environment validation**. No HSM, cloud KMS account, external liboqs installation, test suite, build, or paper compilation was executed as part of this completion pass.

## 2. PKCS#11 HSM

`src/aegistrace/signing/hsm.py` now contains a concrete Ed25519 PKCS#11 path that:

- opens a read/write PKCS#11 session;
- authenticates using the configured PIN when required;
- requires Edwards-curve key-generation and EdDSA mechanisms;
- generates a token-resident key pair;
- marks the private key sensitive and non-extractable;
- retains only public-key material and a deterministic object identifier on the host side;
- performs signing through the token `CKM_EDDSA` mechanism;
- preserves the public object for historical verification when the private signing object is revoked/destroyed.

**Activation boundary:** a compatible PKCS#11 v3-capable token/module and credentials are required. Vendor-specific mechanism/curve encoding compatibility must be validated on the selected device.

## 3. AWS KMS

The AWS path now performs managed asymmetric key creation, public-key retrieval, remote signing, remote verification, disable/revocation state, and active-state resolution.

The default AegisTrace AWS configuration uses `ECC_NIST_EDWARDS25519` with `ED25519_SHA_512`. The backend also accepts configurable AWS KMS asymmetric key specs and maps supported algorithms into scheme-labelled AegisTrace signatures.

AWS KMS currently documents asymmetric signing support including Ed25519 and ML-DSA key specifications and signing algorithms.

## 4. Azure Key Vault

The Azure path now:

- creates an EC P-256 signing/verification key;
- requests hardware protection by default;
- derives the public SPKI/PEM representation from the returned public coordinates;
- uses `CryptographyClient` for remote ES256 signing and verification;
- disables the key through Key Vault key properties on revocation.

**Activation boundary:** an Azure Key Vault/Managed HSM endpoint, credential and appropriate key permissions are required.

## 5. Google Cloud KMS

The Google Cloud path now:

- creates an `ASYMMETRIC_SIGN` CryptoKey using `EC_SIGN_P256_SHA256`;
- requests HSM protection by default, with software protection configurable;
- resolves the first key version and retrieves its public key;
- signs SHA-256 digests through `asymmetric_sign`;
- verifies signatures locally against the KMS-returned public key;
- disables the CryptoKeyVersion on revocation.

**Activation boundary:** a GCP project, location, existing key ring, credentials and KMS permissions are required.

## 6. ML-DSA-65

`src/aegistrace/signing/pqc.py` now provides live liboqs-based:

- algorithm availability resolution;
- key-pair generation;
- secret-key export for controlled migration workflows;
- message signing;
- public-key verification;
- AegisTrace-labelled signature serialization.

The implementation selects the standardized liboqs mechanism `ML-DSA-65`.

## 7. SLH-DSA SHA2-128s

The same module now provides live liboqs-based key generation, signing and verification for the SHA2-128s SLH-DSA target. The current liboqs standardized mechanism name `SLH_DSA_PURE_SHA2_128S` is preferred, with the former SPHINCS+ SHA2-128s-simple mechanism name retained as a compatibility candidate for older liboqs builds.

## 8. Full-Validation Dependency Profile

`pyproject.toml` now includes `liboqs-python>=0.16,<0.17` in the `test-full` profile so a future authorized full validation does not silently skip the new ML-DSA and SLH-DSA round-trip tests solely because the PQC runtime was omitted from the validation environment.

HSM/KMS live tests remain target-environment tests because actual token/cloud credentials and infrastructure are external dependencies. The unit corpus includes credential-free contract coverage where appropriate.

## 9. Status Vocabulary

| Capability | Source status | External/live status |
|---|---|---|
| PKCS#11 Ed25519 | IMPLEMENTED | DEVICE VALIDATION PENDING* |
| AWS KMS signing | IMPLEMENTED | CREDENTIALED VALIDATION PENDING* |
| Azure Key Vault signing | IMPLEMENTED | CREDENTIALED VALIDATION PENDING* |
| Google Cloud KMS signing | IMPLEMENTED | CREDENTIALED VALIDATION PENDING* |
| ML-DSA-65 / liboqs | IMPLEMENTED | FRESH RUNTIME VALIDATION PENDING* |
| SLH-DSA SHA2-128s / liboqs | IMPLEMENTED | FRESH RUNTIME VALIDATION PENDING* |

> `*` The asterisk marks an external activation or fresh-validation boundary, not an unimplemented feature.

## 10. Primary Technical References

- AWS KMS `Sign` API: https://docs.aws.amazon.com/kms/latest/APIReference/API_Sign.html
- AWS KMS key-spec reference: https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-choose-key-spec.html
- Azure Key Vault `KeyClient.create_ec_key`: https://learn.microsoft.com/en-us/python/api/azure-keyvault-keys/azure.keyvault.keys.keyclient
- Azure Key Vault `CryptographyClient`: https://learn.microsoft.com/en-us/python/api/azure-keyvault-keys/azure.keyvault.keys.crypto.cryptographyclient
- Google Cloud KMS Python client: https://docs.cloud.google.com/python/docs/reference/cloudkms/latest/google.cloud.kms_v1.services.key_management_service.KeyManagementServiceClient
- Google Cloud KMS algorithms: https://docs.cloud.google.com/kms/docs/algorithms
- Open Quantum Safe liboqs-python: https://github.com/open-quantum-safe/liboqs-python
- Open Quantum Safe liboqs signature identifiers: https://github.com/open-quantum-safe/liboqs/blob/main/src/sig/sig.h
- PyKCS11 project/API reference: https://github.com/LudovicRousseau/PyKCS11

## 11. Validation Constraint

This completion record does **not** claim that the modified branch has passed a new runtime suite. The last executed complete baseline remains 113/113 on 2026-08-02. The source changes in this record require a future controlled validation before they may be promoted from `IMPLEMENTED / UNVALIDATED` to a newly verified release state.
