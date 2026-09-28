# 13.1 SharePoint Architectural Concepts

## Core Concept
SharePoint is an enterprise content management and data platform built on an object hierarchy. Unlike traditional relational database systems or flat cloud object storage (like AWS S3), SharePoint fuses structured relational data (Lists), unstructured file management (Document Libraries), metadata enrichment, role-based access control, and graphical user interfaces into a unified workspace.

## Key SharePoint Concepts & Terms
- **Site Collection / Site**: The root administrative and security boundary within a tenant holding lists, libraries, and subsites.
- **SharePoint List**: A tabular data structure of rows (list items) and typed columns (text, choice, lookup, currency) similar to a relational database table.
- **Document Library**: A specialized list whose items are binary files (PDFs, docs, images) associated with typed metadata columns and version history.
- **View**: A saved SQL-like projection specifying filtering (`$filter`), sorting (`$orderby`), and column selection (`$select`).
- **Internal Field Name**: The immutable API identifier of a column created upon initial declaration, distinct from the mutable user-facing Display Name.

## Practical Theory: Object Hierarchy vs Relational Databases
In a traditional SQL database, tables are purely logical schemas hosted inside an engine. In SharePoint, data exists within a strict organizational tree: `Tenant -> Site Collection -> Subsite -> List/Library -> Folder -> Item/File`. Security permissions can be inherited down this hierarchy or broken at any node. Recognizing whether a requirement calls for structured fields (List) or binary storage with versions (Library) prevents anti-patterns such as attaching critical PDFs to list rows without document lifecycle management.

## Connection to What Was Built
This folder establishes the structural foundation for SharePoint operations: `TRAINING_SITE_SPEC.md` provides an end-to-end specification for an Engineering Operations site with asset lists and manual libraries; `OBJECT_MAPPING.md` delivers a decision framework matching business requirements to specific SharePoint structural components.
