-- Table: public.activity

-- DROP TABLE public.activity;

CREATE TABLE public.activity
(
    "activityCode" integer NOT NULL,
    id serial NOT NULL,
    id_social_worker integer NOT NULL,
    CONSTRAINT activity_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.activity
    OWNER to postgres;

-- Table: public.ngo

-- DROP TABLE public.ngo;

CREATE TABLE public.ngo
(
    id serial NOT NULL,
    "coordinatorId" integer NOT NULL,
    name character varying NOT NULL,
    "postalAddress" text NOT NULL,
    "emailAddress" character varying NOT NULL,
    "phoneNumber" character varying NOT NULL,
    "logoUrl" character varying NOT NULL,
    balance integer NOT NULL DEFAULT 0,
    "socialWorkerCount" integer NOT NULL DEFAULT 0,
    "childrenCount" integer NOT NULL DEFAULT 0,
    "registerDate" date NOT NULL,
    "lastUpdateDate" date NOT NULL,
    "isActive" boolean NOT NULL DEFAULT true,
    "isDeleted" boolean NOT NULL DEFAULT false,
    city integer NOT NULL,
    country integer NOT NULL,
    "currentSocialWorkerCount" integer NOT NULL DEFAULT 0,
    "currentChildrenCount" integer NOT NULL DEFAULT 0,
    website character varying,
    CONSTRAINT ngo_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.ngo
    OWNER to postgres;

-- Table: public.social_worker

-- DROP TABLE public.social_worker;

CREATE TABLE public.social_worker
(
    id serial NOT NULL,
    "generatedCode" character varying NOT NULL,
    id_ngo integer NOT NULL,
    id_type integer NOT NULL,
    "firstName" character varying,
    "lastName" character varying NOT NULL,
    "userName" character varying NOT NULL,
    password character varying NOT NULL,
    "birthCertificateNumber" character varying,
    "idNumber" character varying NOT NULL,
    "idCardUrl" character varying,
    "passportNumber" character varying,
    "birthDate" date,
    "phoneNumber" character varying NOT NULL,
    "emergencyPhoneNumber" character varying NOT NULL,
    "emailAddress" character varying NOT NULL,
    "telegramId" character varying NOT NULL,
    "postalAddress" text,
    "avatarUrl" character varying NOT NULL,
    "childCount" integer NOT NULL DEFAULT 0,
    "needCount" integer NOT NULL DEFAULT 0,
    "bankAccountNumber" character varying,
    "bankAccountShebaNumber" character varying,
    "bankAccountCardNumber" character varying,
    "registerDate" date NOT NULL,
    "lastUpdateDate" date NOT NULL,
    "lastLoginDate" date NOT NULL,
    "lastLogoutDate" date,
    "passportUrl" character varying,
    "isActive" boolean NOT NULL DEFAULT true,
    "isDeleted" boolean NOT NULL DEFAULT false,
    gender boolean NOT NULL,
    city integer,
    country integer,
    "currentChildCount" integer NOT NULL DEFAULT 0,
    "currentNeedCount" integer NOT NULL DEFAULT 0,
    CONSTRAINT social_worker_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_worker
    OWNER to postgres;

-- Table: public.social_worker_type

-- DROP TABLE public.social_worker_type;

CREATE TABLE public.social_worker_type
(
    id serial NOT NULL,
    name character varying NOT NULL,
    privilege integer NOT NULL,
    CONSTRAINT social_worker_type_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_worker_type
    OWNER to postgres;

-- Table: public.child

-- DROP TABLE public.child;

CREATE TABLE public.child
(
    "phoneNumber" character varying NOT NULL,
    nationality character varying,
    "avatarUrl" character varying NOT NULL,
    id serial NOT NULL,
    "housingStatus" character varying,
    "firstName" character varying,
    "lastName" character varying,
    "familyCount" integer,
    education character varying,
    "createdAt" date NOT NULL,
    "birthPlace" character varying,
    address text,
    bio text NOT NULL,
    "voiceUrl" character varying NOT NULL,
    id_ngo integer NOT NULL,
    id_social_worker integer NOT NULL,
    "confirmUser" integer,
    "confirmDate" date,
    "sayName" character varying NOT NULL,
    "generatedCode" character varying NOT NULL,
    city integer NOT NULL,
    country integer NOT NULL,
    gender boolean NOT NULL,
    "birthDate" date,
    status integer,
    "doneNeedCount" integer NOT NULL DEFAULT 0,
    "spentCredit" integer NOT NULL DEFAULT 0,
    "isDeleted" boolean NOT NULL DEFAULT false,
    "isConfirmed" boolean NOT NULL DEFAULT false,
    "bioSummary" text NOT NULL,
    "sayFamilyCount" integer NOT NULL DEFAULT 0,
    "lastUpdate" date NOT NULL,
    "isMigrated" boolean NOT NULL DEFAULT false,
    "migratedId" integer,
    "migrateDate" date,
    CONSTRAINT child_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.child
    OWNER to postgres;

-- Table: public."user"

-- DROP TABLE public."user";

CREATE TABLE public."user"
(
    "firstName" character varying NOT NULL,
    "lastName" character varying NOT NULL,
    credit integer NOT NULL DEFAULT 0,
    "avatarUrl" character varying,
    "phoneNumber" character varying NOT NULL,
    "userName" character varying,
    "createdAt" date NOT NULL,
    "lastUpdate" date NOT NULL,
    "birthDate" date,
    "birthPlace" character varying,
    "flagUrl" character varying,
    "emailAddress" character varying,
    gender boolean,
    "isDeleted" boolean NOT NULL DEFAULT false,
    city integer NOT NULL,
    country integer NOT NULL,
    "lastLogin" date NOT NULL,
    password character varying,
    "spentCredit" integer NOT NULL DEFAULT 0,
    "doneNeedCount" integer NOT NULL DEFAULT 0,
    id serial NOT NULL,
    token character varying,
    CONSTRAINT user_pkey PRIMARY KEY (id),
    CONSTRAINT "user_PhoneNumber_key" UNIQUE ("phoneNumber")

)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."user"
    OWNER to postgres;

-- Table: public.family

-- DROP TABLE public.family;

CREATE TABLE public.family
(
    id serial NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_child integer NOT NULL,
    CONSTRAINT family_pkey PRIMARY KEY (id),
    CONSTRAINT "family1_Id_child_fkey" FOREIGN KEY (id_child)
        REFERENCES public.child (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.family
    OWNER to postgres;

-- Table: public.need

-- DROP TABLE public.need;

CREATE TABLE public.need
(
    id serial NOT NULL,
    name character varying NOT NULL,
    "imageUrl" character varying NOT NULL,
    category integer NOT NULL,
    description text NOT NULL,
    cost integer NOT NULL,
    "affiliateLinkUrl" character varying,
    "createdAt" date NOT NULL,
    receipts character varying,
    progress integer NOT NULL DEFAULT 0,
    paid integer NOT NULL DEFAULT 0,
    "confirmDate" date,
    "confirmUser" integer,
    "isDone" boolean NOT NULL DEFAULT false,
    "isDeleted" boolean NOT NULL DEFAULT false,
    "isConfirmed" boolean NOT NULL DEFAULT false,
    type integer NOT NULL,
    "descriptionSummary" text NOT NULL,
    "lastUpdate" date NOT NULL,
    "isUrgent" boolean NOT NULL,
    CONSTRAINT need_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.need
    OWNER to postgres;

-- Table: public.child_need

-- DROP TABLE public.child_need;

CREATE TABLE public.child_need
(
    id_need integer NOT NULL,
    id serial NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_child integer NOT NULL,
    CONSTRAINT child_need_pkey PRIMARY KEY (id),
    CONSTRAINT "child_need_Id_child_fkey" FOREIGN KEY (id_child)
        REFERENCES public.child (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "child_need_Id_need_fkey" FOREIGN KEY (id_need)
        REFERENCES public.need (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.child_need
    OWNER to postgres;

-- Table: public.need_family

-- DROP TABLE public.need_family;

CREATE TABLE public.need_family
(
    id serial NOT NULL,
    id_family integer NOT NULL,
    id_user integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_need integer NOT NULL,
    CONSTRAINT need_family_pkey PRIMARY KEY (id),
    CONSTRAINT "need_family_Id_family_fkey" FOREIGN KEY (id_family)
        REFERENCES public.family (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "need_family_Id_need_fkey" FOREIGN KEY (id_need)
        REFERENCES public.need (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "need_family_Id_user_fkey" FOREIGN KEY (id_user)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.need_family
    OWNER to postgres;

-- Table: public.payment

-- DROP TABLE public.payment;

CREATE TABLE public.payment
(
    id serial NOT NULL,
    id_user integer NOT NULL,
    amount integer NOT NULL,
    "createdAt" date NOT NULL,
    id_need integer NOT NULL,
    CONSTRAINT payment_pkey PRIMARY KEY (id),
    CONSTRAINT "payment_Id_need_fkey" FOREIGN KEY (id_need)
        REFERENCES public.need (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "payment_Id_user_fkey" FOREIGN KEY (id_user)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.payment
    OWNER to postgres;

-- Table: public.user_family

-- DROP TABLE public.user_family;

CREATE TABLE public.user_family
(
    id serial NOT NULL,
    id_family integer NOT NULL,
    "userRole" integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_user integer NOT NULL,
    CONSTRAINT user_family_pkey PRIMARY KEY (id),
    CONSTRAINT "user_family_Id_family_fkey" FOREIGN KEY (id_family)
        REFERENCES public.family (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "user_family_Id_user_fkey" FOREIGN KEY (id_user)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.user_family
    OWNER to postgres;