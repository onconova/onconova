#!/bin/bash

# Define variables for clarity
OPENAPI_GENERATOR_VERSION="7.12.0"
OPENAPI_INPUT_FILE="openapi.json"
OUTPUT_DIR="generated/pop-api-client"
GENERATOR_GROUP="typescript-angular"
GENERATOR_ALIAS_AS_MODEL="true"

# Define GENERATOR_OPTIONS as an associative array
declare -A GENERATOR_OPTIONS_MAP
GENERATOR_OPTIONS_MAP["npmName"]="pop-api-client"
GENERATOR_OPTIONS_MAP["fileNaming"]="kebab-case"
GENERATOR_OPTIONS_MAP["withInterfaces"]="true"
GENERATOR_OPTIONS_MAP["useSingleRequestParameter"]="true"

# Construct the comma-separated string from the associative array
GENERATOR_OPTIONS_STRING=""
for key in "${!GENERATOR_OPTIONS_MAP[@]}"; do
    if [[ -n "$GENERATOR_OPTIONS_STRING" ]]; then
        GENERATOR_OPTIONS_STRING+=","
    fi
    GENERATOR_OPTIONS_STRING+="${key}=${GENERATOR_OPTIONS_MAP[$key]}"
done

# Assemble the full arguments for the generator
# Note: The docker command needs paths prefixed with /local/
GENERATOR_ARGS_COMMON="-i ${OPENAPI_INPUT_FILE} -g ${GENERATOR_GROUP} -o ${OUTPUT_DIR} --additional-properties ${GENERATOR_OPTIONS_STRING}"
GENERATOR_ARGS_DOCKER="-i /local/${OPENAPI_INPUT_FILE} -g ${GENERATOR_GROUP} -o /local/${OUTPUT_DIR} --additional-properties ${GENERATOR_OPTIONS_STRING}"

# Conditionally add --generate-alias-as-model if set to true
if [[ "${GENERATOR_ALIAS_AS_MODEL}" == "true" ]]; then
    GENERATOR_ARGS_COMMON+=" --generate-alias-as-model"
    # Docker syntax for conditional append: ${VAR:+TEXT} adds TEXT if VAR is not empty/null
    GENERATOR_ARGS_DOCKER+=" --generate-alias-as-model"
fi

# --- Argument Parsing ---
DESIRED_METHOD=""
USAGE="Usage: $0 [npm|docker|java]"

if [[ "$#" -gt 1 ]]; then
    echo "Error: Too many arguments."
    echo "${USAGE}"
    exit 1
elif [[ "$#" -eq 1 ]]; then
    DESIRED_METHOD="$1"
    case "$DESIRED_METHOD" in
        npm|docker|java)
            ;; # Valid method
        *)
            echo "Error: Invalid method specified: ${DESIRED_METHOD}"
            echo "${USAGE}"
            exit 1
            ;;
    esac
fi

# --- Script Logic ---

# Delete existing generated client directory if it exists
echo "Attempting to delete existing generated client: ${OUTPUT_DIR}"
rm -rf "${OUTPUT_DIR}"
if [ $? -eq 0 ]; then
    echo "Successfully deleted ${OUTPUT_DIR}."
else
    echo "Warning: Could not delete ${OUTPUT_DIR}. It might not exist or there are permission issues."
fi

# Function to run npx method
run_npm() {
    echo "Checking for npm..."
    if command -v npm &> /dev/null; then
        echo "npm found. Checking for globally installed openapi-generator-cli..."
        
        # Check if openapi-generator-cli command is available globally
        if ! command -v openapi-generator-cli &> /dev/null; then
            echo "openapi-generator-cli not found globally. Installing it..."
            # Using -g for global installation
            npm install -g @openapitools/openapi-generator-cli
            if [ $? -ne 0 ]; then
                echo "Error: Failed to install @openapitools/openapi-generator-cli globally with npm."
                return 1 # Installation failed
            fi
            echo "Global installation complete."
        else
            echo "openapi-generator-cli already installed globally."
        fi

        # Ensure the desired version is set using the version manager
        echo "Setting openapi-generator-cli version to ${OPENAPI_GENERATOR_VERSION} using version-manager..."
        # The version-manager command sets a specific generator version for the CLI to use.
        # This requires `openapi-generator-cli` itself to be installed.
        openapi-generator-cli version-manager set "${OPENAPI_GENERATOR_VERSION}"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to set openapi-generator-cli version using version-manager."
            return 1
        fi

        echo "Running openapi-generator-cli generate..."
        # Now run the generate command using the globally installed CLI
        openapi-generator-cli generate ${GENERATOR_ARGS_COMMON}
        if [ $? -eq 0 ]; then
            echo "Successfully generated API client using globally installed openapi-generator-cli (npm)."
            return 0 # Success
        Selse
            echo "Error: openapi-generator-cli generate command failed."
            return 1 # Failure
        fi
    else
        echo "npm not found or not executable. Please ensure Node.js and npm are installed."
        return 1 # npm not found
    fi
}

# Function to run docker method
run_docker() {
    echo "Checking for docker..."
    if command -v docker &> /dev/null; then
        echo "Docker found. Attempting to run openapitools/openapi-generator-cli via Docker..."
        docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli:v${OPENAPI_GENERATOR_VERSION} generate ${GENERATOR_ARGS_DOCKER}
        if [ $? -eq 0 ]; then
            echo "Successfully generated API client using Docker."
            return 0 # Success
        else
            echo "Error: Docker openapitools/openapi-generator-cli failed."
            return 1 # Failure
        fi
    else
        echo "Docker not found or not executable."
        return 1 # Failure
    fi
}

# Function to run java method (global openapi-generator)
run_java() {
    echo "Checking for Java installation..."
    # Check if Java is installed and accessible
    if command -v java &> /dev/null; then
        echo "Java found. Proceeding with openapi-generator-cli (Java JAR)."

        local OPENAPI_GENERATOR_CLI_DIR="/opt/openapi-generator-cli"
        local OPENAPI_GENERATOR_CLI_JAR="${OPENAPI_GENERATOR_CLI_DIR}/openapi-generator-cli-${OPENAPI_GENERATOR_VERSION}.jar"
        # Create the directory if it doesn't exist
        if [ ! -d "${OPENAPI_GENERATOR_CLI_DIR}" ]; then
            echo "Creating directory: ${OPENAPI_GENERATOR_CLI_DIR}"
            mkdir -p "${OPENAPI_GENERATOR_CLI_DIR}"
            chown "${USER}":"${USER}" "${OPENAPI_GENERATOR_CLI_DIR}" # Ensure current user has permissions
        fi

        echo "Checking for openapi-generator-cli-${OPENAPI_GENERATOR_VERSION}.jar at ${OPENAPI_GENERATOR_CLI_JAR}..."
        # Check if the specific version of the JAR exists
        if [ ! -f "${OPENAPI_GENERATOR_CLI_JAR}" ]; then
            echo "JAR file not found. Downloading openapi-generator-cli-${OPENAPI_GENERATOR_VERSION}.jar..."
            curl -L https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/${OPENAPI_GENERATOR_VERSION}/openapi-generator-cli-${OPENAPI_GENERATOR_VERSION}.jar -o "${OPENAPI_GENERATOR_CLI_JAR}"
            if [ $? -ne 0 ]; then
                echo "Error: Failed to download openapi-generator-cli-${OPENAPI_GENERATOR_VERSION}.jar."
                return 1 # Download failed
            fi
            echo "Download complete."
        else
            echo "JAR file already exists."
        fi

        echo "Running openapi-generator with Java..."
        # Use the full path to the downloaded JAR
        java -jar "${OPENAPI_GENERATOR_CLI_JAR}" generate ${GENERATOR_ARGS_COMMON}
        if [ $? -eq 0 ]; then
            echo "Successfully generated API client using Java openapi-generator."
            return 0 # Success
        else
            echo "Error: Failed to run openapi-generator with Java."
            return 1 # Failure
        fi
    else
        echo "Java not found or not executable. Please ensure Java Development Kit (JDK) is installed and in your PATH."
        return 1 # Java not installed
    fi
}


# Execute based on desired method or fall through
if [[ -n "$DESIRED_METHOD" ]]; then
    echo "Generating API client using method: ${DESIRED_METHOD}"
    case "$DESIRED_METHOD" in
        npm)
            run_npm || exit 1
            ;;
        docker)
            run_docker || exit 1
            ;;
        java)
            run_java || exit 1
            ;;
    esac
else
    # No specific method requested, try all in order
    if run_npm; then
        exit 0
    elif run_docker; then
        exit 0
    elif run_java; then
        exit 0
    else
        echo "Error: Could not generate API client. Neither npm, docker, nor a global openapi-generator installation was successful."
        exit 1
    fi
fi

exit 0 # Script finished successfully