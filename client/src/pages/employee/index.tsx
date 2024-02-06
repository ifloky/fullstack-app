import { useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom"
import { useGetEmployeeQuery, useRemoveEmployeeMutation } from "../../app/services/employees";
import { useSelector } from "react-redux";
import { selectUser } from "../../features/auth/authSlice";
import { Layout } from "../../components/layout";
import { Descriptions, Divider, Modal, Space } from "antd";
import { CustomButton } from "../../components/custom-button";
import { DeleteOutlined, EditOutlined } from "@ant-design/icons";
import { ErrorMessage } from "../../components/error-message";
import { Paths } from "../../paths";
import { isErrorWithMessage } from "../../utils/is-error-with-message";

export const Employee = () => {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const params = useParams<{ id: string }>();
  const { data, isLoading } = useGetEmployeeQuery(params.id || "");
  const [removeEmployee] = useRemoveEmployeeMutation();
  const user = useSelector(selectUser);

  if (isLoading) {
    return <span>Loading...</span>
  }

  if (!data) {
    return <Navigate to="/" />
  }

  const showModal = () => {
    setIsModalOpen(true)
  }

  const hideModal = () => {
    setIsModalOpen(false)
  }

  const handleDeleteEmployee = async () => {
    hideModal()
    try {
      await removeEmployee(data.id).unwrap();
      navigate(`${Paths.status}/deleted`)
    } catch (error) {
      const maybeError = isErrorWithMessage(error);
      if (maybeError) {
        setError(error.data.message)
      } else {
        setError("Unknown message")
      }
    }
  }

  return (
    <Layout>
      <Descriptions title="Information about employee" bordered style={{ width: 'min-content', minWidth: '300px' }}>
        <Descriptions.Item label="Name" span={3}>
          {`${data.firstName} ${data.lastName}`}
        </Descriptions.Item>
        <Descriptions.Item label="Age" span={3}>
          {`${data.age} y.o.`}
        </Descriptions.Item>
        <Descriptions.Item label="Address" span={3}>
          {`${data.address}`}
        </Descriptions.Item>
      </Descriptions>
      {
        user?.id === data.userId && (
          <>
            <Divider orientation="left">
              Actions
            </Divider>
            <Space>
              <Link to={`/employee/edit/${data.id}`}>
                <CustomButton
                  shape="round"
                  type="default"
                  icon={<EditOutlined />}
                >
                  Edit
                </CustomButton>
              </Link>
              <CustomButton
                shape="round"
                danger
                icon={<DeleteOutlined />}
                onClick={showModal}
              >
                Delete
              </CustomButton>
            </Space>
          </>
        )
      }
      <ErrorMessage message={error} />
      <Modal
        title="Confirm delete"
        open={isModalOpen}
        onOk={handleDeleteEmployee}
        onCancel={hideModal}
        okText="Confirm"
        cancelText="Cancel"
      >
        Are you sure you want to remove the employee?
      </Modal>
    </Layout>
  )
}
