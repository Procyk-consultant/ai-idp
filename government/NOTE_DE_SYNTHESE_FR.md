---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Fondateur / PDG
Copyright: © 2026 Pierre-Edward Procyk. Tous droits réservés.
Contact: p.procyk.media@gmail.com
File: government/NOTE_DE_SYNTHESE_FR.md
Title: Note de synthèse — AI-IDP
Purpose: Note de synthèse française du projet AI-IDP
Audience: Décideurs politiques, analystes, public canadien et québécois
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Final
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Note de synthèse — AI-IDP

## Identité avant l'autonomie : un cadre universel pour l'identité, la traçabilité et la responsabilité des agents d'intelligence artificielle au Canada

## Sommaire exécutif

Le Canada fait face à un déficit de responsabilité en matière d'intelligence artificielle (IA). Les agents d'IA prennent désormais des décisions importantes dans tous les secteurs de la société canadienne — service à la clientèle, développement logiciel, analyse financière, soutien aux soins de santé, éducation, administration publique et opérations. Ces agents agissent avec des degrés d'autonomie variables, utilisent des modèles fournis par divers fournisseurs, opèrent au-delà des frontières organisationnelles et génèrent du code, des décisions et du contenu qui ont des effets sur les personnes, les systèmes et les institutions canadiennes.

Les mécanismes de responsabilité actuels — journaux d'application, pistes d'audit, historique Git, journaux d'audit des fournisseurs infonuagiques — sont fragmentés, propres à chaque fournisseur et insuffisants pour reconstituer des incidents entre organisations. Ce déficit crée un préjudice réel : après un incident, les organisations ne peuvent pas répondre de façon fiable à la question « quel agent a fait quoi, quand, sur l'autorité de qui, avec quel modèle et quel fournisseur », et les personnes touchées ne peuvent pas attribuer le préjudice à une partie responsable précise.

AI-IDP est un cadre canadien universel proposé qui comble ce déficit. Le cadre exige que tout agent d'IA utilisé, créé, déployé, distribué, contrôlé, exécuté ou rendu disponible au Canada possède : un identifiant d'acteur d'IA permanent et unique ; des identifiants d'instance d'exécution ; des liens traçables avec le fournisseur, le modèle, le déploiement, le contrôleur, le principal, l'agent parent, les sous-agents délégués, les tâches, les actions, les outils et les ressources ; un historique permanent, à ajout unique, infalsifiable ; des preuves de qualité pour le code et les systèmes créés ou modifiés par l'IA ; un modèle de registre à niveaux ; une auditabilité indépendante ; une capacité de reconstitution d'incidents ; une responsabilité juridique ; et des preuves de conformité.

Le principe normatif central du cadre est : **sans identité d'acteur d'IA valide, pas d'exploitation légitime de l'agent**.

## Contexte juridique canadien

Le cadre s'appuie sur le droit canadien actuel : la Loi sur la protection des renseignements personnels et les documents électroniques (LPRPDE, S.C. 2000, c. 5) ; la Loi sur la protection des renseignements personnels (L.R.C. 1985, c. P-21) ; les Lois constitutionnelles de 1867 et de 1982 (y compris la Charte canadienne des droits et libertés) ; le Code criminel ; la Directive du Conseil du Trésor sur les décisions automatisées ; l'Évaluation des facteurs relatifs à la vie privée (EFVP) ; les lois provinciales sur la protection des renseignements personnels (Loi 25 au Québec, PIPA en Colombie-Britannique et en Alberta) ; les appels à l'action de la Commission de vérité et réconciliation ; les principes PCAP® du Centre de gouvernance de l'information des Premières Nations.

**Mise à jour importante (v2.0.0) :** Le projet de loi C-27 (comprenant la Loi sur l'intelligence artificielle et les données, LIAD) est mort au Feuilleton lors de la prorogation du Parlement le 6 janvier 2025. La LIAD n'a pas été adoptée. Aucun projet de loi de remplacement n'avait été déposé en juillet 2026. L'Institut canadien de sécurité de l'intelligence artificielle (ICSA IA / CAISI) a été établi en novembre 2024. La Stratégie nationale en matière d'intelligence artificielle du Canada, intitulée « L'IA pour tous », a été lancée le 4 juin 2026.

## Le cadre AI-IDP

Le cadre comprend : (1) 25 documents de spécification technique ; (2) 14 schémas JSON ; (3) quatre niveaux de conformité (L1 à L4) ; (4) l'implémentation de référence AegisTrace (Python 3.12, signatures Ed25519, registre à chaîne de hachage à ajout unique, 113 tests réussis) ; (5) la suite de tests ; (6) le modèle de menaces ; (7) les analyses d'impact (affaires, RH, société, administration) ; (8) le plan d'implémentation administrative ; (9) le dossier gouvernemental ; (10) l'article arXiv.

## Le principe normatif central

> **Sans identité d'acteur d'IA valide, pas d'exploitation légitime de l'agent.**
> **Sans chaîne d'autorité valide, pas d'action matérielle légitime.**
> **Sans registre de traçabilité permanent, pas d'action modifiante légitime.**
> **Sans chaîne vérifiable utilisateur–agent–modèle–fournisseur, pas de prétention d'exploitation responsable de l'IA.**
> **Sans preuve de qualité exécutée, pas de prétention que le code ou les systèmes générés par l'IA sont vérifiés, testés, sécuritaires, conformes ou prêts pour la production.**

Il s'agit de l'objectif juridique proposé. Ce n'est **pas** le droit canadien actuel.

## Mesures de protection de la vie privée

Le cadre comprend : minimisation ; limitation des fins ; pseudonymisation (identifiants d'utilisateur et de principal pseudonymes par défaut) ; scellement des renseignements (renseignements sensibles scellés et à accès contrôlé) ; séparation du contenu (métadonnées permanentes minimales et engagements cryptographiques, sans contenu en clair) ; contrôle d'accès (accès aux enregistrements scellés consigné et auditable) ; correction et révocation (corrections et révocations sous forme de nouveaux événements signés) ; transparence (entrées publiques du registre n'exposant que les champs non sensibles) ; recours (mécanisme documenté pour les différends, les corrections et les révocations).

## Gouvernance des données autochtones

Le cadre reconnaît la souveraineté des données autochtones. Les dispositions de gouvernance des données autochtones respectent : les principes PCAP® (Propriété, Contrôle, Accès, Possession) du Centre de gouvernance de l'information des Premières Nations ; la distinction entre les Premières Nations, les Inuits et les Métis ; les appels à l'action de la CVR (particulièrement les appels 43 à 44 sur la Déclaration des Nations Unies sur les droits des peuples autochtones et les appels 7, 18, 19 sur la santé autochtone) ; l'accès communautaire aux données des communautés autochtones. **La consultation avec les détenteurs de droits est une condition préalable à l'implémentation.**

## Recommandations

1. Adopter AI-IDP comme Norme nationale du Canada par l'intermédiaire du Conseil canadien des normes.
2. Intégrer l'enregistrement AI-IDP à l'Évaluation des facteurs relatifs à la vie privée du Conseil du Trésor.
3. Établir des niveaux de conformité échelonnés (L1 à L4) avec des organismes de certification sectoriels.
4. Établir une autorité nationale de registre AI-IDP avec des accords de fédération provinciaux.
5. Établir des profils de conformité pour les petits développeurs et les projets open source.
6. Établir des options d'application (sanctions civiles, suspension de service, interdiction d'approvisionnement, responsabilité civile, conséquences probatoires).
7. Édicter la Loi proposée sur l'identité et la traçabilité des acteurs d'IA.
8. Établir des règles de signalement d'incidents.
9. Établir des cadres d'assurance et de responsabilité.
10. Mener une consultation publique par un processus multicanal.

## Conclusion

AI-IDP est un cadre canadien universel proposé pour l'identité permanente des acteurs d'IA, la traçabilité permanente, la délégation, l'assurance qualité et l'exploitation responsable de l'IA. Le cadre comble le déficit de responsabilité dans la gouvernance de l'IA canadienne. Les 23 invariants du cadre tiennent tous sous test. L'implémentation de référence réussit les 113 tests, dont les tests ciblés de sécurité, de confidentialité, de permanence et de conformité. Le succès du cadre dépend de l'adoption de normes nationales, de l'accord fédéral-provincial, de l'établissement d'organismes de certification sectoriels, du développement du marché de l'assurance, de la consultation publique et de la surveillance démocratique continue.

© 2026 Pierre-Edward Procyk. Cognitive Industries — Les Industries Cognitives. Tous droits réservés.
